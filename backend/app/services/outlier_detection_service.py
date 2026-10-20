import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.db.models.normalized_order import NormalizedOrder
from typing import List, Dict, Any

class OutlierDetectionService:
    @staticmethod
    def detect(db: Session, valid_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        warnings = []
        if not valid_records:
            return warnings
            
        # Lấy danh sách tên sản phẩm duy nhất trong đợt đồng bộ này
        product_names = list(set([str(r['product_name']) for r in valid_records if 'product_name' in r]))
        if not product_names:
            return warnings
            
        # Truy vấn dữ liệu lịch sử từ database
        history = db.query(
            NormalizedOrder.product_name,
            NormalizedOrder.unit_price,
            NormalizedOrder.quantity
        ).filter(NormalizedOrder.product_name.in_(product_names)).all()
        
        if not history:
            return warnings
            
        # Đưa vào DataFrame để tính toán bằng pandas
        df_history = pd.DataFrame(history, columns=["product_name", "unit_price", "quantity"])
        
        # Nhóm theo tên sản phẩm, tính số lượng bản ghi, trung bình và độ lệch chuẩn
        stats = df_history.groupby("product_name").agg(
            count=("product_name", "size"),
            price_mean=("unit_price", "mean"),
            price_std=("unit_price", "std"),
            qty_mean=("quantity", "mean"),
            qty_std=("quantity", "std")
        ).reset_index()
        
        # Chỉ xét các sản phẩm có >= 10 bản ghi lịch sử
        stats_filtered = stats[stats['count'] >= 10]
        
        # Chuyển đổi thành dictionary để tra cứu nhanh (key = product_name)
        stats_dict = stats_filtered.set_index("product_name").to_dict(orient="index")
        
        for record in valid_records:
            p_name = str(record.get('product_name', ''))
            
            if p_name in stats_dict:
                p_stats = stats_dict[p_name]
                
                # 1. Phát hiện Outlier cho Đơn giá (unit_price)
                price = float(record.get('unit_price', 0))
                price_mean = p_stats['price_mean']
                price_std = p_stats['price_std']
                
                # std có thể là NaN nếu variance = 0 (tất cả giá trị giống nhau), bỏ qua hoặc xử lý
                if pd.notna(price_std) and price_std > 0:
                    z_price = (price - price_mean) / price_std
                    if abs(z_price) > 3:
                        warnings.append({
                            "type": "unit_price",
                            "product_name": p_name,
                            "actual_value": price,
                            "historical_mean": round(price_mean, 2),
                            "z_score": round(z_price, 2),
                            "message": f"Sản phẩm '{p_name}': Đơn giá {price:,.0f} bất thường (TB lịch sử: {price_mean:,.0f}, Z = {z_price:.1f})."
                        })
                
                # 2. Phát hiện Outlier cho Số lượng (quantity)
                qty = float(record.get('quantity', 0))
                qty_mean = p_stats['qty_mean']
                qty_std = p_stats['qty_std']
                
                if pd.notna(qty_std) and qty_std > 0:
                    z_qty = (qty - qty_mean) / qty_std
                    if abs(z_qty) > 3:
                        warnings.append({
                            "type": "quantity",
                            "product_name": p_name,
                            "actual_value": qty,
                            "historical_mean": round(qty_mean, 2),
                            "z_score": round(z_qty, 2),
                            "message": f"Sản phẩm '{p_name}': Số lượng {qty} bất thường (TB lịch sử: {qty_mean:.1f}, Z = {z_qty:.1f})."
                        })
                        
        return warnings
