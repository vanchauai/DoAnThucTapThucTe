from sqlalchemy import Column, Integer, String, DateTime, Date
from sqlalchemy.sql import func
from app.db.database import Base

class AlertHistory(Base):
    __tablename__ = "alert_history"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False, index=True) # e.g., 'anomaly_revenue'
    alert_date = Column(Date, nullable=False, index=True) # The date the alert was sent
    created_at = Column(DateTime(timezone=True), server_default=func.now())
