from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Service health status"""

    model_config = ConfigDict(extra="forbid")

    status: Literal["healthy", "degraded"] = Field(
        default="healthy", description="Overall service health"
    )
    service: str = "FinOpsGuard Agent"
    version: str = "1.0.0"


class CostCreate(BaseModel):
    """Input model for creating cost record with POST /costs"""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "month": "2026-03",
                "aws_spend": 4200.00,
                "total_budget": 5000.00,
                "allocation_period": "Monthly",
            }
        },
    )

    month: str = Field(
        ..., pattern=r"^\d{4}-\d{2}$", description="Month in YYYY-MM format"
    )
    aws_spend: float = Field(..., ge=0, description="AWS spend for the month in USD")
    total_budget: float = Field(..., gt=0, description="Total allocated budget in USD")
    allocation_period: Literal["Monthly"] = Field(
        ..., description="Budget allocation period"
    )


class CostResponse(BaseModel):
    """Output model for a cost record with computed budget utilization"""

    model_config = ConfigDict(extra="forbid")

    id: int = Field(..., description="Database record ID")
    month: str
    aws_spend: float
    total_budget: float
    allocation_period: str
    budget_used_pct: float = Field(
        ..., description="Computation formula: aws_spend / total_budget * 100"
    )


class ReportRecord(BaseModel):
    """Single record within a report response"""

    month: str
    aws_spend: float
    total_budget: float
    allocation_period: str
    budget_used_pct: float


class ForecastPoint(BaseModel):
    """Single Holt's Damped Trend forecast point returned by the /report endpoint"""

    month: str
    spend: float
    budget: float
    pct: float


class ReportResponse(BaseModel):
    """Full report with cost data, Holt's Damped Trend forecast, and LLM-generated analysis"""

    records: list[ReportRecord]
    forecast: list[ForecastPoint] = Field(
        default_factory=list,
        description="3-month Holt's Damped Trend forecast computed server-side",
    )
    analysis: str = Field(..., description="LLM-generated or fallback cost analysis")
