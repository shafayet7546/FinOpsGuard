from fastapi import FastAPI, HTTPException
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
    description= "Guard your cloud spend and sustainability— monitor costs, assess infrastructure carbon impact, and receive automated alerts with actionable optimization insights.",
    version="1.0.0",
    docs_url="/docs",
)


# health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["monitoring health"])
async def health_check():
    """returns default service status, version, and metadata"""
    return HealthResponse()

# -------------------------------------------------------------------------------------------------------------------------------------
# GET costs endpoint - allows for retrieval of applicable cloud metric values from database
@app.get("/costs", response_model=CloudMetricsResponse, tags=["finops"])
async def get_monthly_costs(db: Session = Depends(get_db)):
    """* Return latest cloud metrics: monthly aws spend, carbon emissions, and budget utilization percentage

        * For convenient testing, demo data is currently provided, however feel free to use `POST /cost` to add new data for db persistence checks"""
    cost = db.query(Cost).order_by(Cost.id.desc()).first()
    if not cost:
        raise HTTPException(
            status_code=404,
            detail = "No cost records found. Use POST /costs to create a record first."
        )
    return CloudMetricsResponse(id=cost.id, month=cost.month, aws_spend=cost.aws_spend, carbon_kg= cost.carbon_kg, budget_used_pct=cost.budget_used_pct)

# POST costs endpoint - allows for input of 'accepted' values into database
# testing purposes: will be automated
@app.post("/costs", response_model=CloudMetricsResponse, tags=["finops"])
async def create_cost_record(cost_data: CloudMetricsResponse, db: Session = Depends(get_db)):
    """Create a new cost record"""
    db_cost = Cost(
        month=cost_data.month,
        aws_spend=cost_data.aws_spend,
        carbon_kg=cost_data.carbon_kg,
        budget_used_pct=cost_data.budget_used_pct
    )
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)

    return CloudMetricsResponse(
        id = db_cost.id,
        month=db_cost.month,
        aws_spend=db_cost.aws_spend,
        carbon_kg=db_cost.carbon_kg,
        budget_used_pct=db_cost.budget_used_pct
    )

# DELETE costs endpoint - allow deletion of entire row associated to explicit id, in database
@app.delete("/costs/{cost_id}", tags=["finops"])
async def delete_cost_record(cost_id: int, db: Session = Depends(get_db)):
    """delete """
    cost = db.query(Cost).filter(Cost.id == cost_id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Cost record does not exist")

    db.delete(cost)
    db.commit()
    return {"message": f"Cost record {cost_id} deleted successfully"}
# -------------------------------------------------------------------------------------------------------------------------------------

# carbon endpoint
# currently retrieves manually ingested data in db
@app.get("/carbon", response_model=CarbonReportResponse, tags=["finops"])
async def get_carbon_report(db: Session = Depends(get_db)):
    """return carbon assessment, kg CO2, and optimization recommendation"""
    carbon = db.query(Carbon).order_by(Carbon.id.desc()).first()
    if not carbon:
            raise HTTPException(
                status_code= 404, 
                detail= "No carbon records found. Use POST /carbon to create a record first."
            )
    # expect to automate recommendations in accordance to carbon score
    return CarbonReportResponse(id = carbon.id, carbon_score=carbon.carbon_score, kg_co2=carbon.kg_co2, recommendation=carbon.recommendation)

# manual ingestion endpoint (automation planned)
@app.post("/carbon", response_model=CarbonReportResponse, tags=["finops"])
async def create_carbon_record(carbon_data: CarbonReportResponse, db: Session = Depends(get_db)):
    """Create a new carbon record"""
    db_carbon = Carbon(
        carbon_score=carbon_data.carbon_score,
        kg_co2=carbon_data.kg_co2,
        recommendation=carbon_data.recommendation
    )
    db.add(db_carbon)
    db.commit()
    db.refresh(db_carbon)

    return CarbonReportResponse(
        id = db_carbon.id,
        carbon_score=db_carbon.carbon_score,
        kg_co2=db_carbon.kg_co2,
        recommendation=db_carbon.recommendation
    )

# report generation endpoint 
@app.get("/report", response_model=ReportResponse, tags=["finops"])
async def generate_report():
    """testing: return mock status message, generated report url (stored in S3) and generated timestamp"""
    return ReportResponse(
        message="Report generated and stored in S3 successfully",
        report_url=None,
        generated_at="2026-03-15T12:00:00Z",
    )
