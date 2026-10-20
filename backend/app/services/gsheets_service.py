import gspread
import pandas as pd
import json
from google.oauth2.service_account import Credentials
from typing import Dict, List, Any, Tuple
from app.core.config import settings
from app.services.excel_service import DataValidator

def get_gspread_client():
    if not settings.GOOGLE_APPLICATION_CREDENTIALS:
        raise ValueError("Google Application Credentials not configured")
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    credentials = Credentials.from_service_account_file(
        settings.GOOGLE_APPLICATION_CREDENTIALS, scopes=scopes
    )
    return gspread.authorize(credentials)

def get_service_account_email() -> str:
    """Lấy email của Service Account từ file JSON cấu hình"""
    if not settings.GOOGLE_APPLICATION_CREDENTIALS:
        return ""
    try:
        with open(settings.GOOGLE_APPLICATION_CREDENTIALS, 'r') as f:
            data = json.load(f)
            return data.get("client_email", "")
    except Exception:
        return ""

def process_google_sheet(sheet_id: str, column_mapping: Dict[str, str], branch_id: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    try:
        client = get_gspread_client()
    except Exception as e:
        raise ValueError(f"Lỗi cấu hình Service Account: {str(e)}")

    try:
        spreadsheet = client.open_by_key(sheet_id)
    except gspread.exceptions.SpreadsheetNotFound:
        raise ValueError("Không tìm thấy Google Sheet. Vui lòng kiểm tra lại URL hoặc đảm bảo đã share quyền cho Service Account.")
    except gspread.exceptions.APIError as e:
        raise ValueError("Lỗi quyền truy cập API. Có thể chưa bật Google Sheets API hoặc chưa share quyền.")
    except Exception as e:
        raise ValueError(f"Lỗi khi truy cập Google Sheet: {str(e)}")
    
    all_valid_records = []
    all_errors = []
    
    # Đọc tất cả các tab (worksheet)
    try:
        for worksheet in spreadsheet.worksheets():
            records = worksheet.get_all_records()
            if not records:
                 continue
                
            df = pd.DataFrame(records)
            
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
                
            valid_records, errors = DataValidator.validate_and_normalize(
                df=df,
                column_mapping=column_mapping,
                branch_id=branch_id,
                source_sheet=worksheet.title
            )
            
            all_valid_records.extend(valid_records)
            all_errors.extend([{"sheet": worksheet.title, **err} for err in errors])
            
        if not all_valid_records and not all_errors:
            raise ValueError("Không tìm thấy dữ liệu hợp lệ trong bất kỳ sheet nào. Vui lòng kiểm tra lại cấu trúc Google Sheet.")
    except Exception as e:
        if "Không tìm thấy dữ liệu hợp lệ" in str(e):
             raise
        raise ValueError(f"Lỗi định dạng hoặc đọc dữ liệu: {str(e)}")
        
    return all_valid_records, all_errors
