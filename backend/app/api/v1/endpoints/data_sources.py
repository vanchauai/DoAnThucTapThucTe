from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Any, List
import shutil
import os
import json

from app.api import deps
from app.db.models.user import User
from app.db.models.data_source import DataSource
from app.schemas.data_source import DataSourceCreate, DataSource as DataSourceSchema, DataSourceInDBBase
from app.services.excel_service import process_excel_file
from app.services.gsheets_service import process_google_sheet
from app.db.models.normalized_order import NormalizedOrder

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("", include_in_schema=False)
@router.get("/")
def get_data_sources(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Lấy danh sách các nguồn dữ liệu
    """
    query = db.query(DataSource)
    if current_user.role != "admin":
        query = query.filter(DataSource.branch_id == current_user.branch_id)
        
    sources = query.all()
    result_data = []
    for s in sources:
        result_data.append({
            "id": s.id,
            "name": s.name,
            "source_type": s.source_type,
            "config": s.config,
            "column_mapping": s.column_mapping,
            "branch_id": s.branch_id,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "status": s.status,
            "error_message": s.error_message,
            "last_synced_at": s.last_synced_at.isoformat() if s.last_synced_at else None
        })
    return {
        "data": result_data,
        "total": len(result_data)
    }

@router.post("/upload", response_model=DataSourceSchema)
def upload_excel_source(
    name: str = Form(...),
    column_mapping: str = Form("{}"), # JSON string
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_manager_or_admin)
) -> Any:
    """
    Upload file Excel và lưu cấu hình Data Source
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        mapping_dict = json.loads(column_mapping) if column_mapping else {}
    except json.JSONDecodeError:
        mapping_dict = {}
        
    db_source = DataSource(
        name=name,
        source_type="excel",
        config={"file_path": file_path},
        column_mapping=mapping_dict,
        branch_id=current_user.branch_id if current_user.role != "admin" else "ALL"
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

from app.services.gsheets_service import get_service_account_email
from pydantic import BaseModel
import re

class GSheetCreate(BaseModel):
    name: str
    url: str
    column_mapping: dict = {}

@router.get("/gsheets/service-account-email")
def get_gsheets_email() -> Any:
    email = get_service_account_email()
    if not email:
        raise HTTPException(status_code=500, detail="Service Account chưa được cấu hình. Vui lòng kiểm tra file .env")
    return {"email": email}

@router.post("/gsheets", response_model=DataSourceSchema)
def create_gsheets_source(
    data: GSheetCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_manager_or_admin)
) -> Any:
    """
    Thêm kết nối Google Sheets
    """
    # Extract sheet ID from URL
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', data.url)
    if not match:
        raise HTTPException(status_code=400, detail="URL Google Sheets không hợp lệ. Vui lòng copy đầy đủ URL (có chứa /d/.../).")
    
    sheet_id = match.group(1)
    
    db_source = DataSource(
        name=data.name,
        source_type="google_sheets",
        config={"sheet_id": sheet_id, "url": data.url},
        column_mapping=data.column_mapping,
        branch_id=current_user.branch_id if current_user.role != "admin" else "ALL"
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

@router.post("/{id}/sync")
def sync_data_source(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_manager_or_admin)
) -> Any:
    """
    Đồng bộ dữ liệu từ Data Source vào bảng NormalizedOrder
    """
    source = db.query(DataSource).filter(DataSource.id == id).first()
    if not source:
        raise HTTPException(status_code=404, detail="DataSource not found")
        
    # Phân quyền: Manager chỉ đồng bộ được nguồn của chi nhánh mình (trừ admin)
    if current_user.role == "manager" and source.branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Not enough privileges")
        
    valid_records = []
    errors = []
    
    try:
        if source.source_type == "excel":
            file_path = source.config.get("file_path")
            valid_records, errors = process_excel_file(
                file_path=file_path,
                column_mapping=source.column_mapping,
                branch_id=source.branch_id
            )
        elif source.source_type == "google_sheets":
            sheet_id = source.config.get("sheet_id")
            valid_records, errors = process_google_sheet(
                sheet_id=sheet_id,
                column_mapping=source.column_mapping,
                branch_id=source.branch_id
            )
            
        # --- CROSS-FILE VALIDATION (Việc A) ---
        from app.services.cross_file_validation_service import CrossFileValidationService
        cross_file_warnings = CrossFileValidationService.validate(db, source, valid_records)
        
        # --- OUTLIER DETECTION (Việc B) ---
        from app.services.outlier_detection_service import OutlierDetectionService
        outlier_warnings = OutlierDetectionService.detect(db, valid_records)
            
        # Lưu vào database
        for record in valid_records:
            existing = db.query(NormalizedOrder).filter(NormalizedOrder.order_id == record['order_id']).first()
            if not existing:
                db_order = NormalizedOrder(**record)
                db.add(db_order)
            else:
                for k, v in record.items():
                    setattr(existing, k, v)
        
        source.status = "synced" if len(valid_records) > 0 else "error"
        if len(errors) > 0 and len(valid_records) == 0:
            source.error_message = "Đồng bộ thất bại: Tất cả các dòng đều bị lỗi hoặc file trống."
        elif len(errors) > 0:
            source.error_message = None # Vẫn thành công phần lớn, không ghi đè lỗi
        else:
            source.error_message = None

        from datetime import datetime
        source.last_synced_at = datetime.utcnow()
        
        # Cập nhật thông số của lần đồng bộ này vào config để dùng cho việc so sánh lần sau
        current_rows = len(valid_records)
        current_revenue = sum(float(r.get('total_amount', 0)) for r in valid_records)
        
        # Do source.config là JSON field nên cần tạo dict mới hoặc copy để SQLAlchemy detect thay đổi
        new_config = dict(source.config) if source.config else {}
        new_config['last_sync_rows'] = current_rows
        new_config['last_sync_revenue'] = current_revenue
        source.config = new_config
                
        db.commit()
        
        # Format errors into row_warnings
        row_warnings = []
        for err in errors:
            sheet_name = err.get("sheet", "")
            row_idx = err.get("row", "")
            reasons = ", ".join(err.get("errors", []))
            if sheet_name:
                row_warnings.append(f"Sheet '{sheet_name}' - Dòng {row_idx}: {reasons}")
            else:
                row_warnings.append(f"Dòng {row_idx}: {reasons}")
        
        return {
            "status": source.status,
            "message": "Sync completed",
            "total_rows_processed": len(valid_records) + len(errors),
            "total_rows_success": len(valid_records),
            "total_synced": len(valid_records),
            "total_errors": len(errors),
            "row_warnings": row_warnings,
            "errors_detail": errors[:10], # Giữ lại compatibility với front-end cũ nếu có
            "cross_file_warnings": cross_file_warnings,
            "outlier_warnings": outlier_warnings
        }
    except Exception as e:
        source.status = "error"
        source.error_message = f"Crash during sync: {str(e)}"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.delete("/{id}")
def delete_data_source(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_manager_or_admin)
) -> Any:
    """
    Xóa một Data Source
    """
    source = db.query(DataSource).filter(DataSource.id == id).first()
    if not source:
        raise HTTPException(status_code=404, detail="DataSource not found")
        
    if current_user.role == "manager" and source.branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Not enough privileges")
        
    db.delete(source)
    db.commit()
    return {"message": "Data source deleted successfully"}
