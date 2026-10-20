from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List, Dict
from datetime import datetime, date, timedelta

from app.api import deps
from app.db.models.user import User
from app.db.models.data_source import DataSource
from app.db.models.alert_history import AlertHistory
from app.services.report_service import ReportService
from pydantic import BaseModel

router = APIRouter()

class InsightTableItem(BaseModel):
    label: str
    value: str

class InsightResponse(BaseModel):
    question: str
    answer_text: str
    table: List[InsightTableItem] = []

def format_currency(amount: float) -> str:
    return f"{amount:,.0f}đ".replace(",", ".")

@router.get("/answer", response_model=InsightResponse)
def get_insight_answer(
    question_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    branch_id = current_user.branch_id if current_user.role != "admin" else None
    
    if question_id == "revenue_this_month":
        current_month = datetime.now().strftime("%m/%Y")
        report = ReportService.generate_report(db, "month", current_month, branch_id, current_user.id, save=False)
        summary = report.get("summary", {})
        total_revenue = summary.get("total_revenue", 0)
        percent = summary.get("revenue_change_percent", 0.0)
        
        status = "tăng" if percent >= 0 else "giảm"
        answer = f"Doanh thu tháng {current_month} là {format_currency(total_revenue)}, {status} {abs(percent):.1f}% so với tháng trước."
        
        return {"question": "Doanh thu tháng này so với tháng trước thế nào?", "answer_text": answer, "table": []}

    elif question_id == "top_product":
        current_month = datetime.now().strftime("%m/%Y")
        report = ReportService.generate_report(db, "month", current_month, branch_id, current_user.id, save=False)
        top_products = report.get("top_products", [])
        
        if not top_products:
            return {"question": "Sản phẩm nào bán chạy nhất tháng này?", "answer_text": "Chưa có dữ liệu bán hàng trong tháng này.", "table": []}
            
        top = top_products[0]
        answer = f"Sản phẩm bán chạy nhất là {top['product_name']}, với {top['total_quantity']} sản phẩm bán ra, mang lại {format_currency(top['total_revenue'])}."
        
        table = [{"label": p['product_name'], "value": format_currency(p['total_revenue'])} for p in top_products[:5]]
        return {"question": "Sản phẩm nào bán chạy nhất tháng này?", "answer_text": answer, "table": table}

    elif question_id == "branch_ranking":
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
            
        current_month = datetime.now().strftime("%m/%Y")
        report = ReportService.generate_report(db, "month", current_month, None, current_user.id, save=False)
        branches = report.get("branch_breakdown", [])
        
        if not branches:
            return {"question": "Chi nhánh nào có doanh thu cao nhất?", "answer_text": "Chưa có dữ liệu doanh thu của các chi nhánh.", "table": []}
            
        branches = sorted(branches, key=lambda x: x['total_revenue'], reverse=True)
        top = branches[0]
        answer = f"Chi nhánh có doanh thu cao nhất là {top['branch_name']} với {format_currency(top['total_revenue'])}."
        
        table = [{"label": b['branch_name'], "value": format_currency(b['total_revenue'])} for b in branches]
        return {"question": "Chi nhánh nào có doanh thu cao nhất?", "answer_text": answer, "table": table}

    elif question_id == "forecast":
        current_month = datetime.now().strftime("%m/%Y")
        report = ReportService.generate_report(db, "month", current_month, branch_id, current_user.id, save=False)
        chart_data = report.get("chart_data", [])
        
        forecast_val = 0
        if chart_data and chart_data[-1].get("forecast_revenue") is not None:
            forecast_val = chart_data[-1]["forecast_revenue"]
            
        if forecast_val > 0:
            answer = f"Dựa trên dữ liệu gần đây, dự báo doanh thu các tuần sắp tới dao động ở mức khoảng {format_currency(forecast_val)} mỗi tuần."
        else:
            answer = "Chưa đủ dữ liệu lịch sử để đưa ra dự báo doanh thu."
            
        return {"question": "Xu hướng doanh thu sắp tới dự báo thế nào?", "answer_text": answer, "table": []}

    elif question_id == "data_source_errors":
        query = db.query(DataSource)
        if branch_id:
            query = query.filter(DataSource.branch_id == branch_id)
            
        error_sources = query.filter(DataSource.status == "error").all()
        
        if not error_sources:
            answer = "Tất cả nguồn dữ liệu đều đang hoạt động bình thường."
            table = []
        else:
            names = ", ".join([s.name for s in error_sources])
            answer = f"Có {len(error_sources)} nguồn dữ liệu đang gặp lỗi: {names}."
            table = [{"label": s.name, "value": str(s.error_message or "Lỗi không xác định")} for s in error_sources]
            
        return {"question": "Có nguồn dữ liệu nào đang gặp lỗi không?", "answer_text": answer, "table": table}

    elif question_id == "anomaly_alert":
        seven_days_ago = date.today() - timedelta(days=7)
        alerts = db.query(AlertHistory).filter(
            AlertHistory.alert_type == 'anomaly_revenue',
            AlertHistory.alert_date >= seven_days_ago
        ).order_by(AlertHistory.alert_date.desc()).all()
        
        if not alerts:
            answer = "Tuyệt vời, không phát hiện dữ liệu bất thường hoặc sụt giảm doanh thu đột ngột nào trong 7 ngày qua."
            table = []
        else:
            dates = ", ".join([a.alert_date.strftime("%d/%m/%Y") for a in alerts])
            answer = f"Chú ý: Hệ thống đã phát hiện doanh thu sụt giảm bất thường (>30%) vào các ngày: {dates}."
            table = [{"label": a.alert_date.strftime("%d/%m/%Y"), "value": "Sụt giảm doanh thu"} for a in alerts]
            
        return {"question": "Có phát hiện dữ liệu bất thường nào gần đây không?", "answer_text": answer, "table": table}

    else:
        raise HTTPException(status_code=400, detail="Unknown question_id")
