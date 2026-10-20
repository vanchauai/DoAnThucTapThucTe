from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class DataSourceBase(BaseModel):
    name: str
    source_type: str # 'excel', 'google_sheets'
    config: Dict[str, Any]
    column_mapping: Dict[str, str]
    branch_id: str
    status: str = "pending"
    last_synced_at: Optional[datetime] = None

class DataSourceCreate(DataSourceBase):
    pass

class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    source_type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    column_mapping: Optional[Dict[str, str]] = None
    branch_id: Optional[str] = None

class DataSourceInDBBase(DataSourceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DataSource(DataSourceInDBBase):
    pass
