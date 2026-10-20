import sys
import os

# Add the app directory to the path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal
from app.db.models.normalized_order import NormalizedOrder
from app.db.models.data_source import DataSource

db = SessionLocal()

print("--- DATA SOURCES ---")
for ds in db.query(DataSource).all():
    print(f"ID: {ds.id}, Name: {ds.name}, Status: {ds.status}, Error: {ds.error_message}, Config: {ds.config}")

print("\n--- ORDERS FROM SHEET ---")
orders = db.query(NormalizedOrder).filter(NormalizedOrder.order_id.like('DH00%')).all()
print(f"Total orders from sheet: {len(orders)}")
for o in orders:
    print(f"ID: {o.order_id}, Date: {o.order_date}, Branch: {o.branch_id}".encode('utf-8'))



db.close()
