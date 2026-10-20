import os
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, date
from sqlalchemy import func

from app.db.database import SessionLocal
from app.services.email_service import send_email
from app.services.report_service import ReportService
from app.db.models.normalized_order import NormalizedOrder

scheduler = BackgroundScheduler()

# Dùng để theo dõi việc gửi cảnh báo anomaly, giới hạn 1 lần 1 ngày
last_anomaly_alert_date = None

def generate_excel_report(db, start_date: date, end_date: date) -> str:
    # Query data
    summary = ReportService.get_summary_metrics(db)
    top_products = ReportService.get_top_products(db)
    
    wb = openpyxl.Workbook()
    
    # Sheet 1: Summary
    ws = wb.active
    ws.title = "Summary"
    
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    
    headers = ["Chỉ số", "Giá trị"]
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
        
    ws.cell(row=2, column=1, value="Tổng số đơn hàng").font = Font(bold=True)
    ws.cell(row=2, column=2, value=summary['total_orders'])
    ws.cell(row=3, column=1, value="Tổng doanh thu").font = Font(bold=True)
    ws.cell(row=3, column=2, value=summary['total_revenue'])
    
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 20
    
    # Sheet 2: Top Products
    ws2 = wb.create_sheet(title="Top Products")
    headers2 = ["Tên sản phẩm", "Số lượng bán"]
    for col_num, header in enumerate(headers2, 1):
        cell = ws2.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
        
    for row_num, prod in enumerate(top_products, 2):
        ws2.cell(row=row_num, column=1, value=prod['product_name'])
        ws2.cell(row=row_num, column=2, value=prod['total_quantity'])
        
    ws2.column_dimensions['A'].width = 40
    ws2.column_dimensions['B'].width = 20
    
    # Ensure exports dir
    os.makedirs("exports", exist_ok=True)
    filename = f"exports/daily_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    wb.save(filename)
    return filename

def daily_report_task():
    print(f"[{datetime.now()}] Running daily report task...")
    db = SessionLocal()
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        # Tạo file Excel
        excel_path = generate_excel_report(db, start_date, end_date)
        summary = ReportService.get_summary_metrics(db)
        
        body = f"""
        Xin chào,
        
        Đây là báo cáo tổng hợp tự động từ hệ thống Data Sync & Report.
        
        - Tổng số đơn hàng: {summary['total_orders']}
        - Tổng doanh thu: {summary['total_revenue']:,.2f} VNĐ
        
        Vui lòng xem chi tiết trong file Excel đính kèm.
        
        Trân trọng.
        """
        
        send_email(
            subject=f"Báo cáo doanh thu hàng ngày ({end_date})",
            body=body,
            to_emails=["admin@example.com"], # Trong thực tế có thể query bảng User để lấy admin
            attachment_path=excel_path
        )
        print("Daily report Excel sent successfully!")
    except Exception as e:
        print(f"Error in daily_report_task: {e}")
    finally:
        db.close()

from app.db.models.alert_history import AlertHistory

def anomaly_alert_task():
    print(f"[{datetime.now()}] Running anomaly alert task...")
    db = SessionLocal()
    try:
        current_time = datetime.now()
        today = current_time.date()
        
        # 1. Kiểm tra đã gửi cảnh báo hôm nay chưa (lưu trong DB)
        existing_alert = db.query(AlertHistory).filter(
            AlertHistory.alert_type == 'anomaly_revenue',
            AlertHistory.alert_date == today
        ).first()
        
        if existing_alert:
            print("Đã gửi cảnh báo anomaly hôm nay. Bỏ qua để tránh spam.")
            return
            
        # 2. Tính doanh thu CÙNG MỘT MỐC GIỜ (0h đến thời điểm hiện tại)
        # Sử dụng created_at (thời gian ghi nhận đơn hàng vào hệ thống)
        today_start = datetime.combine(today, datetime.min.time())
        today_revenue = db.query(func.sum(NormalizedOrder.total_amount)).filter(
            NormalizedOrder.created_at >= today_start,
            NormalizedOrder.created_at <= current_time
        ).scalar() or 0
        
        # Tính doanh thu 7 ngày trước (chỉ tính từ 0h đến giờ tương ứng của ngày đó)
        past_revenue = 0
        for i in range(1, 8):
            past_date = today - timedelta(days=i)
            past_start = datetime.combine(past_date, datetime.min.time())
            past_end = datetime.combine(past_date, current_time.time())
            
            day_rev = db.query(func.sum(NormalizedOrder.total_amount)).filter(
                NormalizedOrder.created_at >= past_start,
                NormalizedOrder.created_at <= past_end
            ).scalar() or 0
            past_revenue += day_rev
            
        avg_past_revenue = past_revenue / 7
        
        if avg_past_revenue > 0:
            drop_ratio = (avg_past_revenue - today_revenue) / avg_past_revenue
            if drop_ratio > 0.3: # Rớt hơn 30%
                body = f"""
                CẢNH BÁO BẤT THƯỜNG DOANH THU
                
                Hệ thống phát hiện doanh thu hôm nay (tính đến {current_time.strftime('%H:%M')}) là {today_revenue:,.2f} VNĐ.
                Con số này sụt giảm nghiêm trọng so với trung bình 7 ngày trước trong cùng khung giờ ({avg_past_revenue:,.2f} VNĐ).
                Mức giảm: {drop_ratio*100:.1f}%
                
                Vui lòng kiểm tra lại hệ thống bán hàng hoặc tình trạng đồng bộ dữ liệu nguồn.
                """
                send_email(
                    subject="[Khẩn cấp] Cảnh báo doanh thu sụt giảm",
                    body=body,
                    to_emails=["admin@example.com"]
                )
                
                # Ghi lịch sử gửi cảnh báo vào DB
                alert_record = AlertHistory(alert_type='anomaly_revenue', alert_date=today)
                db.add(alert_record)
                db.commit()
                print("Anomaly alert sent and saved to DB!")
    except Exception as e:
        print(f"Error in anomaly_alert_task: {e}")
    finally:
        db.close()

def start_scheduler():
    # Chạy lúc 8h sáng hàng ngày
    scheduler.add_job(daily_report_task, 'cron', hour=8, minute=0, id='daily_report')
    
    # Chạy kiểm tra anomaly lúc 9, 12, 15, 18h
    scheduler.add_job(anomaly_alert_task, 'cron', hour='9,12,15,18', id='anomaly_alert')
    
    scheduler.start()
    print("Scheduler started with real tasks!")
