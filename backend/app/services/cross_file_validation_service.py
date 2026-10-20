from sqlalchemy.orm import Session
from app.db.models.normalized_order import NormalizedOrder
from typing import List, Dict, Any

class CrossFileValidationService:
    @staticmethod
    def validate(db: Session, current_source: Any, valid_records: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        if not valid_records:
            return warnings
            
        # 1. Phát hiện order_id trùng lặp giữa các nguồn/chi nhánh khác nhau
        order_ids = [str(r['order_id']) for r in valid_records]
        
        existing_orders = db.query(NormalizedOrder.order_id, NormalizedOrder.branch_id)\
                            .filter(NormalizedOrder.order_id.in_(order_ids)).all()
        
        existing_map = {str(o[0]): str(o[1]) for o in existing_orders}
        
        for record in valid_records:
            order_id = str(record['order_id'])
            current_branch = str(record.get('branch_id', ''))
            
            if order_id in existing_map:
                existing_branch = existing_map[order_id]
                # Nếu khác branch -> Lỗi nghiệp vụ lớn (trùng mã đơn hàng của 2 chi nhánh)
                if existing_branch != current_branch:
                    warnings.append(f"Đơn hàng '{order_id}': Bị trùng với chi nhánh '{existing_branch}'.")
                # Nếu cùng branch thì là update dữ liệu bình thường, không cần cảnh báo
        
        # 2. Phát hiện độ lệch bất thường (tăng/giảm đột biến so với lần trước)
        current_rows = len(valid_records)
        current_revenue = sum(float(r.get('total_amount', 0)) for r in valid_records)
        
        config = current_source.config or {}
        last_sync_rows = config.get('last_sync_rows')
        last_sync_revenue = config.get('last_sync_revenue')
        
        if last_sync_rows is not None and last_sync_rows > 0:
            row_diff = (current_rows - last_sync_rows) / last_sync_rows
            if row_diff < -0.5:
                warnings.append(f"Số lượng dòng giảm mạnh ({row_diff * 100:.1f}%). Lần trước: {last_sync_rows}, Hiện tại: {current_rows}. Cảnh báo thiếu dữ liệu.")
            elif row_diff > 1.0:
                warnings.append(f"Số lượng dòng tăng đột biến (+{row_diff * 100:.1f}%). Lần trước: {last_sync_rows}, Hiện tại: {current_rows}.")
                
        if last_sync_revenue is not None and last_sync_revenue > 0:
            rev_diff = (current_revenue - last_sync_revenue) / last_sync_revenue
            if rev_diff < -0.5:
                warnings.append(f"Tổng doanh thu giảm mạnh ({rev_diff * 100:.1f}%). Lần trước: {last_sync_revenue:,.0f}, Hiện tại: {current_revenue:,.0f}.")
        
        return list(set(warnings)) # Loại bỏ trùng lặp nếu có
