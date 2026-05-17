from sqlalchemy import Column, DateTime, Float, Integer, String, func

from app.database import Base


class Cost(Base):
    """Stores monthly cloud spend and budget allocation data"""

    __tablename__ = "costs"
    id = Column(Integer, primary_key=True, index=True)
    month = Column(String, index=True)
    aws_spend = Column(Float)
    total_budget = Column(Float)
    allocation_period = Column(String)
    created_at = Column(DateTime, server_default=func.now())
