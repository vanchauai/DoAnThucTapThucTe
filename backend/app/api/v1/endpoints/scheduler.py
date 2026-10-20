from fastapi import APIRouter, Depends
from typing import Any
from app.api import deps
from app.db.models.user import User

router = APIRouter()

@router.get("/jobs")
def get_scheduler_jobs(
    current_user: User = Depends(deps.get_current_admin)
) -> Any:
    """
    Lấy danh sách các jobs đang chạy ngầm. Chỉ Admin có quyền.
    """
    from app.services.scheduler_service import scheduler
    jobs = scheduler.get_jobs()
    return [{"id": job.id, "name": job.name, "next_run_time": job.next_run_time} for job in jobs]

from pydantic import BaseModel, Field

class SchedulerConfigUpdate(BaseModel):
    daily_report_hour: int = Field(..., ge=0, le=23, description="Giờ chạy báo cáo hàng ngày (0-23)")
    daily_report_minute: int = Field(0, ge=0, le=59, description="Phút chạy báo cáo hàng ngày (0-59)")

from sqlalchemy.orm import Session
from app.db.models.audit_log import AuditLog

@router.post("/config")
def config_scheduler(
    config: SchedulerConfigUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin)
) -> Any:
    """
    Cấu hình lịch chạy. Chỉ Admin có quyền.
    """
    from app.services.scheduler_service import scheduler
    
    # Đổi lịch cho daily_report_task
    scheduler.reschedule_job('daily_report', trigger='cron', hour=config.daily_report_hour, minute=config.daily_report_minute)
    
    # Ghi Audit Log vào database
    audit_log = AuditLog(
        user_id=current_user.id,
        action="UPDATE_SCHEDULER_CONFIG",
        detail=f"Changed daily_report schedule to {config.daily_report_hour}:{config.daily_report_minute:02d}"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": f"Đã đổi lịch báo cáo hàng ngày sang {config.daily_report_hour}:{config.daily_report_minute:02d}"}
