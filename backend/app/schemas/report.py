from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ReportCreate(BaseModel):
    period_type: str
    period_value: str
    branch_id: Optional[str] = None
    save: bool = True

class ReportHistoryItem(BaseModel):
    id: int
    report_name: str
    period_type: str
    period_value: str
    branch_id: Optional[str] = None
    created_by: int
    created_at: datetime
    file_url_excel: Optional[str] = None
    file_url_pdf: Optional[str] = None

    class Config:
        from_attributes = True

class ReportDataResponse(BaseModel):
    summary: Dict[str, Any]
    chart_data: List[Dict[str, Any]]
    top_products: List[Dict[str, Any]]
    branch_breakdown: List[Dict[str, Any]]
