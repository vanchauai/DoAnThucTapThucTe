from sqlalchemy import Column, Integer, String, Date, Float, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class NormalizedOrder(Base):
    __tablename__ = "normalized_orders"

    # order_id không để primary_key đơn thuần vì có thể nhiều đơn trùng mã từ các nguồn khác nhau?
    # Theo requirement, order_id là unique. Ta sẽ set PK là id tự tăng, order_id là unique=True
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(100), unique=True, index=True, nullable=False)
    order_date = Column(Date, nullable=False, index=True)
    product_name = Column(String(255), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    customer_name = Column(String(255), nullable=True)
    branch_id = Column(String(100), nullable=False, index=True)
    source_sheet = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
