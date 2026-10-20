from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String(255), nullable=False)
    period_type = Column(String(50), nullable=False)
    period_value = Column(String(100), nullable=False)
    branch_id = Column(String(50), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Lưu toàn bộ JSON kết quả báo cáo để lịch sử tải lại nhanh chóng
    data = Column(JSON, nullable=True)
    
    file_url_excel = Column(String(255), nullable=True)
    file_url_pdf = Column(String(255), nullable=True)
