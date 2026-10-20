from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models.normalized_order import NormalizedOrder
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import pandas as pd
import math
from fastapi import HTTPException
import calendar

class ReportService:
    @staticmethod
    def get_summary_metrics(db: Session, branch_id: str = None, start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """
        Lấy các chỉ số tổng quan cơ bản: tổng đơn, tổng doanh thu
        """
        query = db.query(
            func.count(NormalizedOrder.order_id).label("total_orders"),
            func.sum(NormalizedOrder.total_amount).label("total_revenue")
        )
        
        if branch_id:
            query = query.filter(NormalizedOrder.branch_id == branch_id)
        if start_date:
            query = query.filter(NormalizedOrder.order_date >= start_date)
        if end_date:
            query = query.filter(NormalizedOrder.order_date <= end_date)
            
        # Loại trừ ngày hôm nay
        query = query.filter(NormalizedOrder.order_date < date.today())
            
        result = query.first()
        total_orders = int(result.total_orders or 0)
        total_revenue = float(result.total_revenue or 0)
        
        return {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "avg_revenue_per_order": float(total_revenue / total_orders) if total_orders > 0 else 0.0
        }
        
    @staticmethod
    def get_top_products(db: Session, branch_id: str = None, start_date: date = None, end_date: date = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Top 5 sản phẩm bán chạy nhất (theo quantity)
        """
        query = db.query(
            NormalizedOrder.product_name,
            func.sum(NormalizedOrder.quantity).label("total_quantity"),
            func.sum(NormalizedOrder.total_amount).label("total_revenue")
        ).group_by(NormalizedOrder.product_name)
        
        if branch_id:
            query = query.filter(NormalizedOrder.branch_id == branch_id)
        if start_date:
            query = query.filter(NormalizedOrder.order_date >= start_date)
        if end_date:
            query = query.filter(NormalizedOrder.order_date <= end_date)
            
        # Loại trừ ngày hôm nay
        query = query.filter(NormalizedOrder.order_date < date.today())
            
        results = query.order_by(func.sum(NormalizedOrder.quantity).desc()).limit(limit).all()
        
        return [{"product_name": str(r.product_name), "total_quantity": float(r.total_quantity or 0), "total_revenue": float(getattr(r, 'total_revenue', 0) or 0)} for r in results]

    @staticmethod
    def get_revenue_by_branch(db: Session, branch_id: str = None, start_date: date = None, end_date: date = None) -> List[Dict[str, Any]]:
        """
        Doanh thu theo chi nhánh
        """
        query = db.query(
            NormalizedOrder.branch_id,
            func.sum(NormalizedOrder.total_amount).label("total_revenue")
        ).group_by(NormalizedOrder.branch_id)
        
        if branch_id:
            query = query.filter(NormalizedOrder.branch_id == branch_id)
        if start_date:
            query = query.filter(NormalizedOrder.order_date >= start_date)
        if end_date:
            query = query.filter(NormalizedOrder.order_date <= end_date)
            
        # Loại trừ ngày hôm nay
        query = query.filter(NormalizedOrder.order_date < date.today())
            
        results = query.all()
        return [{"branch_id": str(r.branch_id), "total_revenue": float(r.total_revenue or 0)} for r in results]

    @staticmethod
    def parse_period(period_type: str, period_value: str) -> tuple[date, date]:
        """
        Hàm hỗ trợ parse khoảng thời gian từ period_value
        Ví dụ: 
        period_type="month", period_value="08/2026"
        period_type="year", period_value="2026"
        """
        try:
            if period_value == "all":
                return None, None
                
            if period_type == "month":
                m, y = period_value.split('/')
                start_date = date(int(y), int(m), 1)
                last_day = calendar.monthrange(int(y), int(m))[1]
                end_date = date(int(y), int(m), last_day)
            elif period_type == "year":
                y = int(period_value)
                start_date = date(y, 1, 1)
                end_date = date(y, 12, 31)
            else:
                # Fallback, nếu không hỗ trợ thì coi như không filter
                return None, None
            return start_date, end_date
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid period_value format")

    @staticmethod
    def generate_report(db: Session, period_type: str, period_value: str, branch_id: str = None, user_id: int = None, save: bool = True) -> Dict[str, Any]:
        """
        Tạo báo cáo chi tiết, bao gồm summary, chart_data, top_products, branch_breakdown
        Và lưu vào DB nếu save = True.
        """
        from app.db.models.report import Report
        
        start_date, end_date = ReportService.parse_period(period_type, period_value)
        
        # 1. Tính toán summary cho kỳ hiện tại
        summary = ReportService.get_summary_metrics(db, branch_id, start_date, end_date)
        
        # 2. Tính Tăng trưởng doanh thu (Revenue Change Percent)
        revenue_change_percent = 0.0
        if start_date and end_date:
            try:
                # Tính chính xác kỳ trước dựa trên period_type
                if period_type == "month":
                    # Lùi 1 tháng
                    m = start_date.month - 1
                    y = start_date.year
                    if m == 0:
                        m = 12
                        y -= 1
                    prev_start_date, prev_end_date = ReportService.parse_period("month", f"{m:02d}/{y}")
                elif period_type == "year":
                    # Lùi 1 năm
                    prev_start_date, prev_end_date = ReportService.parse_period("year", str(start_date.year - 1))
                else:
                    # Fallback dùng delta ngày
                    delta = end_date - start_date
                    prev_end_date = start_date - pd.Timedelta(days=1)
                    prev_start_date = prev_end_date - delta
                
                prev_summary = ReportService.get_summary_metrics(db, branch_id, prev_start_date, prev_end_date)
                if prev_summary['total_revenue'] > 0:
                    revenue_change_percent = ((summary['total_revenue'] - prev_summary['total_revenue']) / prev_summary['total_revenue']) * 100
            except Exception:
                pass # Bỏ qua nếu lỗi tính toán kỳ trước
        
        summary["revenue_change_percent"] = revenue_change_percent
        
        # 3. Tính toán top_products và branch_breakdown
        top_products = ReportService.get_top_products(db, branch_id, start_date, end_date)
        branch_breakdown = ReportService.get_revenue_by_branch(db, branch_id, start_date, end_date)
        
        # 4. Chart data và Moving Average (Forecast) bằng pandas
        # Lấy TẤT CẢ data (có thể giới hạn 1 khoảng lớn để tiết kiệm bộ nhớ)
        query_all = db.query(
            NormalizedOrder.order_date,
            NormalizedOrder.total_amount
        ).filter(NormalizedOrder.order_date < date.today())
        
        if branch_id:
            query_all = query_all.filter(NormalizedOrder.branch_id == branch_id)
            
        records = query_all.all()
        chart_data = []
        if records:
            df = pd.DataFrame(records, columns=['order_date', 'total_amount'])
            df['order_date'] = pd.to_datetime(df['order_date'])
            
            # Group by tùy theo period_type
            if period_type == "year":
                # Nhóm theo tháng trong cả lịch sử để tính MA
                df_grouped = df.groupby(df['order_date'].dt.to_period('M'))['total_amount'].sum().reset_index()
                df_grouped['label'] = df_grouped['order_date'].dt.strftime('%m/%Y')
                window = 3 # 3 tháng
            elif period_type == "month":
                # Nhóm theo tuần
                df_grouped = df.groupby(df['order_date'].dt.to_period('W'))['total_amount'].sum().reset_index()
                df_grouped['label'] = df_grouped['order_date'].dt.start_time.dt.strftime('%d/%m/%Y')
                window = 3 # 3 tuần
            else:
                # Nhóm theo ngày
                df_grouped = df.groupby(df['order_date'].dt.to_period('D'))['total_amount'].sum().reset_index()
                df_grouped['label'] = df_grouped['order_date'].dt.strftime('%d/%m/%Y')
                window = 3 # 3 ngày
                
            df_grouped = df_grouped.sort_values('order_date')
            
            # Tính Moving Average
            df_grouped['forecast_revenue'] = df_grouped['total_amount'].rolling(window=window, min_periods=1).mean()
            
            # Xử lý NaN thành None để parse JSON thành null
            df_grouped = df_grouped.where(pd.notnull(df_grouped), None)
            
            for _, row in df_grouped.iterrows():
                # Lọc ra chỉ lấy các chart item nằm TRONG khoảng thời gian report hoặc vài data point gần đó
                # (để đơn giản, hiện tại ta lấy hết để thấy rõ đường xu hướng)
                
                chart_data.append({
                    "label": str(row['label']),
                    "revenue": float(row['total_amount']) if row['total_amount'] is not None else 0.0,
                    "forecast_revenue": float(row['forecast_revenue']) if row['forecast_revenue'] is not None else None
                })
        else:
            # Nếu không có data
            chart_data = [{"label": "No Data", "revenue": 0.0, "forecast_revenue": None}]
            
        report_data = {
            "summary": summary,
            "chart_data": chart_data,
            "top_products": top_products,
            "branch_breakdown": branch_breakdown
        }
        
        # Lưu vào DB nếu save = True
        if save:
            db_report = Report(
                report_name=f"Báo cáo doanh thu {period_value}",
                period_type=period_type,
                period_value=period_value,
                branch_id=branch_id,
                created_by=user_id,
                data=report_data
            )
            db.add(db_report)
            db.commit()
            db.refresh(db_report)
        
        return report_data
