from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.db.database import Base

class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False) # 'excel', 'google_sheets'
    config = Column(JSON, nullable=False) # Lưu đường dẫn file hoặc sheet_id
    column_mapping = Column(JSON, nullable=False) # Cấu hình mapping cột gốc sang cột chuẩn
    branch_id = Column(String(100), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="pending", nullable=False)
    error_message = Column(String(1000), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
