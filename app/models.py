from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class HealthResponse(BaseModel):
    """Service health status - returned with GET /health endpoint"""

    model_config = ConfigDict(
        extra="forbid",  # security: prevent unexpected fields in health check response
        json_schema_extra={
            "example": {
                "status": "healthy",
                "service": "FinOpsGuard",
                "version": "1.0.0",
            }
        },
    )
    # health status is mock for now, will implement actual health checks soon
    status: Literal["healthy", "degraded"] = Field(
        default="healthy", description="Overall health status of the service"
    )
    service: str = "FinOpsGuard"
    version: str = "1.0.0"


class CloudMetricsResponse(BaseModel):
    """Monthly cloud cost and carbon metrics - returned with GET /costs endpoint"""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "month": "2026-03",
                "aws_spend": 317.50,
                "carbon_kg": 128.6,
                "budget_used_pct": 31.75,
            }
        },
    )

    month: str = Field(
        ..., pattern=r"^\d{4}-\d{2}$", description="Month in YYYY-MM format"
    )
    aws_spend: float = Field(..., ge=0, description="AWS spend for the month")
    carbon_kg: float = Field(..., ge=0, description="Estimated CO2 emissions in kg")
    budget_used_pct: float = Field(
        ..., ge=0, le=100, description="Percentage of budget used"
    )


class CarbonReportResponse(BaseModel):
    """Carbon impact assessment - returned by GET /carbon endpoint"""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "carbon_score": "low",
                "kg_co2": 128.6,
                "recommendation": "Switch to t4g.micro instance for 30%+ savings",
            }
        },
    )

    carbon_score: Literal["low", "medium", "high"] = Field(
        ..., description="Carbon impact score based on emissions"
    )
    kg_co2: float = Field(..., ge=0, description="Estimated CO2 emissions in kg")
    recommendation: str = Field(
        ...,
        min_length=10,
        description="Optimization recommendation for the cloud resource",
    )


class ReportResponse(BaseModel):
    """PDF report generation status - returned by GET /report endpoint"""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "message": "PDF report generated and stored in S3 successfully",
                "report_url": None,
                "generated_at": "2026-03-15T12:00:00Z",
            }
        },
    )
    message: str = Field(..., description="Status message")
    report_url: str | None = Field(None, description="S3 URL of the generated PDF")
    generated_at: str = Field(..., description="Generated timestamp")
