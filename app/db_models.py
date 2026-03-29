from sqlalchemy import Column, Float, Integer, String
from app.database import Base

# table in database for /cost api
class Cost(Base):
    '''Stores monthly cloud spend and carbon metrics'''
    table_name = "costs"
    id = Column(Integer, primary_key=True, index=True)
    month = Column(String, index=True)
    aws_spend = Column(Float)
    carbon_kg = Column(Float)
    budget_used_pct = Column(Float)

class Carbon(Base):
    """Stores carbon score and applicable recommendation"""
    table_name = "carbon_report"
    id = Column(Integer, primary_key=True, index=True)
    carbon_score = Column(String)
    kg_co2 = Column(Float)
    recommendation = Column(String)