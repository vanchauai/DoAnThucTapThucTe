import pandas as pd
from typing import Dict, List, Any, Tuple
from datetime import datetime

class DataValidator:
    REQUIRED_COLUMNS = ['order_id', 'order_date', 'product_name', 'quantity', 'unit_price']
    
    # Auto alias mapping for flexibility
    COLUMN_ALIASES = {
        "order_id": ["order_id", "mã đơn hàng", "mã đơn", "mã đh", "order id", "ma don hang", "ma_don_hang", "id", "order_no", "mã hóa đơn", "so hoa don", "ma don", "ma dh"],
        "order_date": ["order_date", "ngày đặt", "ngày đặt hàng", "ngày", "ngay dat", "ngay_dat", "order date", "date", "created_at", "ngày lập"],
        "product_name": ["product_name", "tên sản phẩm", "sản phẩm", "tên sp", "ten san pham", "ten_san_pham", "product name", "product", "item", "item_name", "tên hàng", "mặt hàng"],
        "quantity": ["quantity", "số lượng", "sl", "so luong", "so_luong", "qty", "amount"],
        "unit_price": ["unit_price", "đơn giá", "giá", "giá bán", "don gia", "don_gia", "unit price", "price", "thành tiền đơn giá"],
        "customer_name": ["customer_name", "khách hàng", "tên khách hàng", "ten khach hang", "ten_khach_hang", "tên kh", "customer name", "customer", "buyer", "người mua"]
    }
    
    @staticmethod
    def validate_and_normalize(df: pd.DataFrame, column_mapping: Dict[str, str], branch_id: str, source_sheet: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        valid_records = []
        errors = []
        
        # Build effective reverse mapping
        reverse_mapping = {}
        if column_mapping:
            for std_col, orig_col in column_mapping.items():
                if orig_col in df.columns:
                    reverse_mapping[orig_col] = std_col
        
        # Auto-match remaining columns if not explicitly mapped
        for std_col, aliases in DataValidator.COLUMN_ALIASES.items():
            if std_col not in reverse_mapping.values():
                for col in df.columns:
                    clean_col = str(col).strip().lower()
                    if clean_col in [a.lower() for a in aliases] and col not in reverse_mapping:
                        reverse_mapping[col] = std_col
                        break
        
        # Chỉ giữ lại các cột có trong mapping
        cols_to_keep = [col for col in df.columns if col in reverse_mapping]
        df_mapped = df[cols_to_keep].rename(columns=reverse_mapping)
        
        # Kiểm tra ở mức độ sheet xem có thiếu cột bắt buộc nào không
        missing_cols = [col for col in DataValidator.REQUIRED_COLUMNS if col not in df_mapped.columns]
        if missing_cols:
            orig_cols = list(df.columns)
            errors.append({
                "row": "ALL",
                "errors": [f"Missing required columns in sheet: {', '.join(missing_cols)}. Original columns found: {orig_cols}"],
                "data": {}
            })
            return valid_records, errors
        
        for index, row in df_mapped.iterrows():
            row_dict = row.to_dict()
            row_errors = []
            
            # Xử lý mặc định cho quantity nếu bị bỏ trống (thường gặp trong thực tế, ngầm hiểu là 1)
            if 'quantity' in row_dict and (pd.isna(row_dict['quantity']) or str(row_dict['quantity']).strip() == ""):
                row_dict['quantity'] = 1
                
            # Xử lý mặc định cho đơn giá (nếu trống có thể là hàng tặng/khuyến mãi, ngầm hiểu là 0)
            if 'unit_price' in row_dict and (pd.isna(row_dict['unit_price']) or str(row_dict['unit_price']).strip() == ""):
                row_dict['unit_price'] = 0

            # Kiểm tra các cột bắt buộc
            for col in DataValidator.REQUIRED_COLUMNS:
                if col not in row_dict or pd.isna(row_dict[col]) or str(row_dict[col]).strip() == "":
                    row_errors.append(f"thiếu dữ liệu ở cột '{col}'")
            
            # Nếu có lỗi thiếu trường thì bỏ qua dòng này luôn
            if row_errors:
                errors.append({"row": index + 2, "errors": row_errors, "data": row_dict})
                continue
                
            # Validate Data Types & Logic
            try:
                quantity = float(row_dict['quantity'])
                if quantity < 0:
                    row_errors.append("cột số lượng có giá trị âm vô lý")
            except (ValueError, TypeError):
                row_errors.append(f"cột số lượng có giá trị '{row_dict['quantity']}', không phải là số hợp lệ")
                
            try:
                unit_price = float(row_dict['unit_price'])
                if unit_price < 0:
                    row_errors.append("cột đơn giá có giá trị âm vô lý")
            except (ValueError, TypeError):
                row_errors.append(f"cột đơn giá có giá trị '{row_dict['unit_price']}', không phải là số hợp lệ")
                
            try:
                # Xử lý ngày tháng
                order_date = pd.to_datetime(row_dict['order_date']).date()
            except Exception:
                row_errors.append(f"ngày tháng sai định dạng")

            if row_errors:
                errors.append({"row": index + 2, "errors": row_errors, "data": row_dict})
                continue
                
            # Tạo record chuẩn
            valid_record = {
                "order_id": str(row_dict['order_id']),
                "order_date": order_date,
                "product_name": str(row_dict['product_name']),
                "quantity": float(quantity),
                "unit_price": float(unit_price),
                "total_amount": float(quantity) * float(unit_price),
                "customer_name": str(row_dict.get('customer_name', '')) if not pd.isna(row_dict.get('customer_name')) else None,
                "branch_id": branch_id,
                "source_sheet": source_sheet
            }
            valid_records.append(valid_record)
            
        return valid_records, errors

def find_header_row(df: pd.DataFrame) -> int:
    """Tìm dòng có khả năng là header nhất (chứa các từ khóa cột quen thuộc)"""
    # Nếu header mặc định (dòng 0) đã có vẻ đúng (có ít nhất 2 cột alias)
    def count_matches(row_values):
        matches = 0
        for val in row_values:
            val_str = str(val).lower().strip()
            for aliases in DataValidator.COLUMN_ALIASES.values():
                if val_str in [a.lower() for a in aliases]:
                    matches += 1
                    break
        return matches

    if count_matches(df.columns) >= 2:
        return 0

    # Tìm trong 20 dòng đầu tiên
    best_row_idx = -1
    max_matches = 0
    for i, row in df.head(20).iterrows():
        matches = count_matches(row.values)
        if matches > max_matches:
            max_matches = matches
            best_row_idx = i

    if max_matches >= 2:
        return best_row_idx + 1 # +1 vì df.iterrows() index từ 0, tương đương dòng 1 trong data
    return 0

def process_excel_file(file_path: str, column_mapping: Dict[str, str], branch_id: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    all_valid_records = []
    all_errors = []
    
    # Đọc tất cả các sheet
    xls = pd.ExcelFile(file_path)
    for sheet_name in xls.sheet_names:
        # Đọc nháp để tìm header
        df_temp = pd.read_excel(xls, sheet_name=sheet_name, nrows=25)
        if df_temp.empty and len(df_temp.columns) == 0:
            continue
            
        header_idx = find_header_row(df_temp)
        
        if header_idx > 0:
            df = pd.read_excel(xls, sheet_name=sheet_name, header=header_idx)
        else:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
        # Kiểm tra xem sheet này có vẻ là sheet dữ liệu không (ít nhất phải map được 2 cột)
        mapped_cols = 0
        for col in df.columns:
            clean_col = str(col).strip().lower()
            for aliases in DataValidator.COLUMN_ALIASES.values():
                if clean_col in [a.lower() for a in aliases]:
                    mapped_cols += 1
                    break
        
        # Nếu sheet không có ít nhất 2 cột khớp với dữ liệu yêu cầu, coi như sheet ghi chú/hướng dẫn
        if mapped_cols < 2:
            continue
        
        # Drop các dòng trống hoàn toàn
        df = df.dropna(how='all')
        
        valid_records, errors = DataValidator.validate_and_normalize(
            df=df,
            column_mapping=column_mapping,
            branch_id=branch_id,
            source_sheet=sheet_name
        )
        all_valid_records.extend(valid_records)
        all_errors.extend([{"sheet": sheet_name, **err} for err in errors])
        
    if not all_valid_records and not all_errors:
         raise ValueError("Không tìm thấy dữ liệu hợp lệ trong bất kỳ sheet nào. Vui lòng kiểm tra lại cấu trúc file.")
        
    return all_valid_records, all_errors
