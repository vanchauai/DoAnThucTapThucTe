import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.gsheets_service import get_gspread_client

try:
    client = get_gspread_client()
    spreadsheet = client.open_by_key('1E8rsfpZkLAkb8JN4i690FF5zdgTjfJntuop56EaigYY')
    worksheets = spreadsheet.worksheets()
    for ws in worksheets:
        print("WORKSHEET:", ws.title)
        records = ws.get_all_records()
        for r in records[:5]:
            print(str(r).encode('utf-8'))
except Exception as e:
    print("ERROR:", e)
