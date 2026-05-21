import os
import random
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# OpenAI dependency check, built to be gracefully disabled if not installed
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from app.database import Base, SessionLocal, engine
from app.db_models import Cost
from app.models import (
    CostCreate,
    CostResponse,
    ForecastPoint,
    HealthResponse,
    ReportRecord,
    ReportResponse,
)

Base.metadata.create_all(bind=engine)


def _calculate_budget_used_pct(aws_spend: float, total_budget: float) -> float:
    """Calculate budget utilization percentage"""
    if total_budget <= 0:
        return 0.0
    return round(aws_spend / total_budget * 100, 1)


def _to_cost_response(record: Cost) -> CostResponse:
    """Convert a Cost ORM row into a CostResponse."""
    return CostResponse(
        id=record.id,
        month=record.month,
        aws_spend=record.aws_spend,
        total_budget=record.total_budget,
        allocation_period=record.allocation_period,
        budget_used_pct=_calculate_budget_used_pct(
            record.aws_spend, record.total_budget
        ),
    )


def _get_ordered_cost_records(db: Session) -> list[Cost]:
    """Fetch cost records which are ordered chronologically by: month and id."""
    return db.query(Cost).order_by(Cost.month.asc(), Cost.id.asc()).all()


def get_db():
    """DB session dependency — ensures closure after use"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(
    title="FinOpsGuard Agent",
    description=(
        "AI-powered cloud cost intelligence — monitor AWS spend, forecast "
        "budget utilization, and receive LLM-generated optimization recommendations."
    ),
    version="1.0.0",
    docs_url="/docs",
)

app.mount("/static", StaticFiles(directory="assets"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    file_path = Path(__file__).parent / "index.html"
    return file_path.read_text(encoding="utf-8")


@app.get("/health", response_model=HealthResponse, tags=["monitoring"])
async def health_check():
    """Return service health status and version metadata"""
    return HealthResponse()


# ── Costs CRUD ──


@app.get("/costs", response_model=list[CostResponse], tags=["finops"])
async def get_costs(db: Session = Depends(get_db)):
    """Return all cost records ordered by month"""
    records = _get_ordered_cost_records(db)
    if not records:
        raise HTTPException(status_code=404, detail="No cost records found.")

    result: list[CostResponse] = []
    for record in records:
        result.append(_to_cost_response(record))

    return result


@app.post("/costs", response_model=CostResponse, status_code=201, tags=["finops"])
async def create_cost(data: CostCreate, db: Session = Depends(get_db)):
    """Create a new cost record"""
    record = Cost(
        month=data.month,
        aws_spend=data.aws_spend,
        total_budget=data.total_budget,
        allocation_period=data.allocation_period,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _to_cost_response(record)


@app.delete("/costs/{cost_id}", tags=["finops"])
async def delete_cost(cost_id: int, db: Session = Depends(get_db)):
    """Delete a single cost record by ID"""
    cost = db.query(Cost).filter(Cost.id == cost_id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Cost record not found")
    db.delete(cost)
    db.commit()
    return {"message": f"Cost record {cost_id} deleted"}


@app.delete("/costs", tags=["finops"])
async def delete_all_costs(db: Session = Depends(get_db)):
    """Clear all cost records (used by frontend reset flows)"""
    db.query(Cost).delete()
    db.commit()
    return {"message": "All cost records deleted"}


# ── Seed Demo Data ──


@app.post("/costs/seed", status_code=201, tags=["finops"])
async def seed_demo_data(db: Session = Depends(get_db)):
    """Seed the database with randomized demo cost data"""
    budget = round(random.uniform(4000, 6000), 2)
    demo = [
        Cost(
            month="2026-01",
            aws_spend=round(budget * random.uniform(0.40, 0.55), 2),
            total_budget=budget,
            allocation_period="Monthly",
        ),
        Cost(
            month="2026-02",
            aws_spend=round(budget * random.uniform(0.60, 0.78), 2),
            total_budget=budget,
            allocation_period="Monthly",
        ),
        Cost(
            month="2026-03",
            aws_spend=round(budget * random.uniform(0.82, 0.96), 2),
            total_budget=budget,
            allocation_period="Monthly",
        ),
        Cost(
            month="2026-04",
            aws_spend=round(budget * random.uniform(0.82, 0.96), 2),
            total_budget=budget,
            allocation_period="Monthly",
        ),
        Cost(
            month="2026-05",
            aws_spend=round(budget * random.uniform(0.82, 0.96), 2),
            total_budget=budget,
            allocation_period="Monthly",
        ),
    ]
    db.add_all(demo)
    db.commit()
    # Return seeded records with computed budget %
    records = _get_ordered_cost_records(db)
    seeded_records: list[dict] = []
    for record in records:
        seeded_records.append(
            {
                "id": record.id,
                "month": record.month,
                "aws_spend": record.aws_spend,
                "total_budget": record.total_budget,
                "allocation_period": record.allocation_period,
                "budget_used_pct": _calculate_budget_used_pct(
                    record.aws_spend, record.total_budget
                ),
            }
        )

    return {
        "message": "Demo data seeded",
        "count": len(demo),
        "records": seeded_records,
    }


# ── Report with LLM Analysis ──


class ForecastEngine:
    """Simple Holt's Damped trend forecasting engine."""

    def __init__(self, alpha: float = 0.4, beta: float = 0.3, phi: float = 0.85):
        self.alpha = alpha
        self.beta = beta
        self.phi = phi

    def project(self, records: list[ReportRecord], months_ahead: int = 3) -> list[dict]:
        """Forecast potential upcoming monthly spend."""
        if len(records) < 2:
            return []

        spends: list[float] = []
        for record in records:
            spends.append(record.aws_spend)

        level = spends[0]
        trend = spends[1] - spends[0]

        for i in range(1, len(spends)):
            prev_level = level
            level = self.alpha * spends[i] + (1 - self.alpha) * (
                level + self.phi * trend
            )
            trend = (
                self.beta * (level - prev_level) + (1 - self.beta) * self.phi * trend
            )

        forecasts: list[dict] = []
        last_budget = records[-1].total_budget
        parts = records[-1].month.split("-")
        year, month = int(parts[0]), int(parts[1])

        for h in range(1, months_ahead + 1):
            month += 1
            if month > 12:
                month = 1
                year += 1
            forecast_month = f"{year}-{month:02d}"

            damped_trend_total = 0.0
            for j in range(1, h + 1):
                damped_trend_total += self.phi**j

            projected_spend = max(0.0, round(level + damped_trend_total * trend, 2))
            projected_pct = _calculate_budget_used_pct(projected_spend, last_budget)

            forecasts.append(
                {
                    "month": forecast_month,
                    "spend": projected_spend,
                    "budget": last_budget,
                    "pct": projected_pct,
                }
            )

        return forecasts


class ReportService:
    """Builds report records, forecast data, and AI analysis."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
        self.forecast_engine = ForecastEngine()

    def build_records(self, db_records: list[Cost]) -> list[ReportRecord]:
        """Convert DB rows into ReportRecord objects with computed budget %."""
        report_records: list[ReportRecord] = []
        for record in db_records:
            budget_used_pct = _calculate_budget_used_pct(
                record.aws_spend, record.total_budget
            )
            report_records.append(
                ReportRecord(
                    month=record.month,
                    aws_spend=record.aws_spend,
                    total_budget=record.total_budget,
                    allocation_period=record.allocation_period,
                    budget_used_pct=budget_used_pct,
                )
            )
        return report_records

    def analyze(self, records: list[ReportRecord]) -> str:
        """Call OpenAI for cost analysis; fall back to deterministic summary if unavailable."""
        if not self.api_key or OpenAI is None:
            return self._fallback_analysis(records)

        try:
            client = OpenAI(api_key=self.api_key)

            data_lines: list[str] = []
            for record in records:
                data_lines.append(
                    f"- {record.month}: ${record.aws_spend:,.2f} spent of ${record.total_budget:,.2f} budget "
                    f"({record.budget_used_pct}% used, {record.allocation_period} allocation)"
                )

            data_text = "\n".join(data_lines)
            user_prompt = (
                f"AWS cloud spend data:\n\n{data_text}\n\n"
                "Deliver an executive cost briefing in this exact structure:\n\n"
                "## Key Findings\n"
                "- List explicit monthly budget spending/percentage utilization of budget in nested bullet points for better visibility"
                "- 2-3 bullet points: the most important spending patterns with exact numbers\n\n"
                "## 3-Month Forecast\n"
                "- Ensure to highlight under heading: 'Holt's Damped Trend algorithm was utilized for short-term forecasting'"
                "- Project spend for each of the next 3 months with dollar amounts\n"
                "- State the projected budget breach month (if any) and the estimated overage\n\n"
                "## Risk Assessment\n"
                "- Rate overall risk: LOW / MODERATE / HIGH / CRITICAL\n"
                "- One sentence explaining why\n\n"
                "## Recommended Actions\n"
                "For each recommendation (give exactly 2):\n"
                "- **Action**: What to do\n"
                "- **Impact**: Estimated savings or risk reduction\n"
                "- **Steps**: 2-3 concrete implementation steps that is a mix of compute/tools/expenditure\n\n"
                "Use markdown. Be concise — no introductions or summaries. Make no mistakes"
            )

            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior FinOps advisor presenting to engineering and financial leadership. "
                            "Be direct, data-driven, and action-oriented. Every insight must tie to "
                            "a dollar impact."
                        ),
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                max_completion_tokens=700,
                temperature=0.4,
            )

            message_content = response.choices[0].message.content
            if message_content is None:
                return self._fallback_analysis(records)
            return message_content
        except Exception:
            return self._fallback_analysis(records)

    def _fallback_analysis(self, records: list[ReportRecord]) -> str:
        """Deterministic summary when the LLM is unavailable."""
        if not records:
            return "No data available for analysis."

        latest = records[-1]
        spends: list[float] = []
        for record in records:
            spends.append(record.aws_spend)

        avg_spend = sum(spends) / len(spends)
        total_change = spends[-1] - spends[0] if len(spends) > 1 else 0
        pct_change = (
            (total_change / spends[0] * 100) if spends[0] > 0 and len(spends) > 1 else 0
        )

        lines = ["## Fallback Summary"]
        lines.append(f"- Avg monthly spend: **${avg_spend:,.0f}**")
        lines.append(f"- Trend: **{pct_change:+.1f}%** from first to latest month")
        lines.append(
            f"- Latest utilization: **{latest.budget_used_pct}%** of ${latest.total_budget:,.0f} budget"
        )

        forecasts = self.forecast_engine.project(records, 3)
        if forecasts:
            first_forecast = forecasts[0]
            lines.append(
                f"- Next month projection: **${first_forecast['spend']:,.0f}** "
                f"({first_forecast['pct']}% of budget)"
            )

            breach_month = None
            for forecast in forecasts:
                if forecast["pct"] > 100:
                    breach_month = forecast["month"]
                    break

            if breach_month:
                lines.append(f"- Projected budget breach month: **{breach_month}**")
        else:
            lines.append("- Forecast unavailable (need at least 2 months of data)")

        risk_pct = forecasts[-1]["pct"] if forecasts else latest.budget_used_pct
        if risk_pct >= 100:
            risk, reason = (
                "CRITICAL",
                "Projected spend exceeds budget within the forecast window.",
            )
        elif risk_pct >= 90:
            risk, reason = (
                "HIGH",
                "Spend is approaching budget ceiling with upward momentum.",
            )
        elif risk_pct >= 75:
            risk, reason = (
                "MODERATE",
                "Utilization is elevated but not yet at critical levels.",
            )
        else:
            risk, reason = "LOW", "Spending is well within budget allocation."

        lines.append(f"- Risk level: **{risk}** ({reason})")
        lines.append("*Warning: AI is currently sleeping and unable to do analysis...*")

        return "\n".join(lines)


report_service = ReportService()


@app.get("/report", response_model=ReportResponse, tags=["finops"])
async def generate_report(db: Session = Depends(get_db)):
    """Generate a cost analysis report with LLM-powered recommendations"""
    records = _get_ordered_cost_records(db)
    if not records:
        raise HTTPException(
            status_code=404,
            detail="No cost data available. Add cost records first.",
        )
    report_records = report_service.build_records(records)
    raw_forecast = report_service.forecast_engine.project(report_records, 3)

    forecast: list[ForecastPoint] = []
    for point in raw_forecast:
        forecast.append(ForecastPoint(**point))

    analysis = report_service.analyze(report_records)
    return ReportResponse(records=report_records, forecast=forecast, analysis=analysis)
