from fastapi import FastAPI
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db_models import Cost, Carbon
from app.models import HealthResponse, CloudMetricsResponse, CarbonReportResponse, ReportResponse
from app.database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine) 

def get_db():
    """DB session dependency - ensures closure after utilization"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title="FinOpsGuard",
    description="Monitor cloud cost, assess infrastructure carbon impact, and receive automated budget alerts with actionable optimization recommendations.",
    version="1.0.0",
    docs_url="/docs",
)


# health check endpoint - returns default service status, version, and metadata
@app.get("/health", response_model=HealthResponse, tags=["monitoring"])
async def health_check():
    return HealthResponse()


# costs endpoint
@app.get("/costs", response_model=CloudMetricsResponse, tags=["finops"])
async def get_monthly_costs(db: Session = Depends(get_db)):
    cost = db.query(Cost).first()
    if not cost:
        return CloudMetricsResponse()
    """return monthly aws spend, carbon emissions, and budget utilization percentage"""
    return CloudMetricsResponse(month=cost.month, aws_spend=cost.aws_spend, carbon_kg= cost.carbon_kg, budget_used_pct=cost.budget_used_pct)


# carbon endpoint
@app.get("/carbon", response_model=CarbonReportResponse, tags=["finops"])
async def get_carbon_report(db: Session = Depends(get_db)):
    carbon = db.query(Carbon).first()
    if not carbon:
        return CarbonReportResponse()
    CarbonReportResponse(carbon_score=carbon.carbon_score, kg_co2=carbon.kg_co2, recommendation=carbon.recommendation)
    """return carbon assessment, kg CO2, and optimization recommendation"""
    # expect to automate recommendations in accordance to carbon score


# report generation endpoint 
@app.get("/report", response_model=ReportResponse, tags=["finops"])
async def generate_report():
    """testing: return mock status message, generated report url (stored in S3) and generated timestamp"""
    return ReportResponse(
        message="Report generated and stored in S3 successfully",
        report_url=None,
        generated_at="2026-03-15T12:00:00Z",
    )
