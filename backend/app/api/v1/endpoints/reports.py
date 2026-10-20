from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any

from app.api import deps
from app.db.models.user import User
from app.db.models.report import Report
from app.services.report_service import ReportService
from app.schemas.report import ReportCreate, ReportDataResponse, ReportHistoryItem

router = APIRouter()

@router.get("/summary")
def get_report_summary(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Lấy báo cáo tổng hợp (Doanh thu, Đơn hàng)
    """
    branch_id = current_user.branch_id if current_user.role != "admin" else None
    
    metrics = ReportService.get_summary_metrics(db, branch_id)
    top_products = ReportService.get_top_products(db, branch_id)
    revenue_by_branch = ReportService.get_revenue_by_branch(db, branch_id)
    
    return {
        "metrics": metrics,
        "top_products": top_products,
        "revenue_by_branch": revenue_by_branch
    }

@router.post("/generate", response_model=ReportDataResponse)
def generate_report(
    report_req: ReportCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Tạo báo cáo chi tiết và lưu lịch sử nếu save=True
    """
    if current_user.role != "admin":
        branch_id = current_user.branch_id
    else:
        branch_id = report_req.branch_id
        
    return ReportService.generate_report(
        db=db,
        period_type=report_req.period_type,
        period_value=report_req.period_value,
        branch_id=branch_id,
        user_id=current_user.id,
        save=report_req.save
    )

@router.get("/history")
def get_report_history(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Lấy lịch sử báo cáo
    """
    query = db.query(Report)
    if current_user.role != "admin":
        query = query.filter(Report.branch_id == current_user.branch_id)
        
    reports = query.order_by(Report.created_at.desc()).all()
    result_data = []
    for r in reports:
        result_data.append({
            "id": r.id,
            "report_name": r.report_name,
            "period_type": r.period_type,
            "period_value": r.period_value,
            "branch_id": r.branch_id,
            "created_by": r.created_by,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "file_url_excel": r.file_url_excel,
            "file_url_pdf": r.file_url_pdf
        })
    return {
        "data": result_data,
        "total": len(result_data)
    }

@router.get("/{id}")
def get_report_detail(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Lấy chi tiết 1 báo cáo
    """
    from fastapi import HTTPException
    
    report = db.query(Report).filter(Report.id == id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    if current_user.role != "admin" and report.branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return report.data

@router.delete("/{id}")
def delete_report(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_manager_or_admin)
) -> Any:
    """
    Xóa báo cáo
    """
    from fastapi import HTTPException
    
    report = db.query(Report).filter(Report.id == id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    if current_user.role == "manager" and report.branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Not enough privileges")
        
    db.delete(report)
    db.commit()
    return {"message": "Report deleted successfully"}
