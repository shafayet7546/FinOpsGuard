from fastapi import FastAPI
from app.models import HealthResponse, CloudMetricsResponse, CarbonReportResponse, ReportResponse

app = FastAPI(
    title="FinOpsGuard",
    description="Personal cloud spend + carbon footprint tracker with budget alerts and optimization recommendations.",
    version="1.0.0",
    docs_url="/docs",
)


# health check endpoint - returns service status, version, and metadata
@app.get("/health", response_model=HealthResponse, tags=["monitoring"])
async def health_check():
    return HealthResponse()


# costs endpoint - returns mock monthly AWS spend, carbon emissions, and budget utilization percentage
@app.get("/costs", response_model=CloudMetricsResponse, tags=["FinOps"])
async def get_monthly_costs():
    """testing: return mock aws spend, carbon emissions, and budget utilization percentage"""
    return CloudMetricsResponse(
        month="2026-03", aws_spend=317.50, carbon_kg=128.6, budget_used_pct=31.75
    )


# carbon endpoint - returns mock carbon impact score, kg CO2 emissions, and optimization recommendation
@app.get("/carbon", response_model=CarbonReportResponse, tags=["FinOps"])
async def get_carbon_report():
    """testing: return mock carbon assessment, kg CO2, and optimization recommendation"""
    return CarbonReportResponse(
        carbon_score="low",
        kg_co2=128.6,
        recommendation="Switch to t4g.micro instance for 30%+ savings",
    )


# report generation endpoint - returns mock status message, generated report url (stored in S3) and generated timestamp
@app.get("/report", response_model=ReportResponse, tags=["FinOps"])
async def generate_report():
    """testing: return mock status message, generated report url (stored in S3) and generated timestamp"""
    return ReportResponse(
        message="Report generated and stored in S3 successfully",
        report_url=None,
        generated_at="2026-03-15T12:00:00Z",
    )
