from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class NormalizedOrderBase(BaseModel):
    order_id: str
    order_date: date
    product_name: str
    quantity: float
    unit_price: float
    total_amount: float
    customer_name: Optional[str] = None
    branch_id: str
    source_sheet: Optional[str] = None

class NormalizedOrderCreate(NormalizedOrderBase):
    pass

class NormalizedOrderInDBBase(NormalizedOrderBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class NormalizedOrder(NormalizedOrderInDBBase):
    pass
