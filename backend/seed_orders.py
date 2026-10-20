import sys
import os
from datetime import date, timedelta
from sqlalchemy.orm import Session
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models.normalized_order import NormalizedOrder
from app.db.models.data_source import DataSource
import random
from datetime import datetime

def seed_data():
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(NormalizedOrder).count() > 0:
            print("Data already exists. Clearing old data for a clean test...")
            db.query(NormalizedOrder).delete()
            db.query(DataSource).filter(DataSource.name == "Dữ liệu test tự động").delete()
            db.commit()

        ds = DataSource(
            name="Dữ liệu test tự động",
            source_type="excel",
            config={"file_path": "mock_data.xlsx"},
            column_mapping={},
            branch_id="ALL",
            status="synced",
            last_synced_at=datetime.utcnow()
        )
        db.add(ds)
        db.commit()

        # Generate 4 months of data (to ensure we have enough past data for a 3-month window MA)
        end_date = date.today()
        start_date = end_date - timedelta(days=120)
        
        products = ["Iphone 15", "MacBook Pro M3", "AirPods Pro", "iPad Air", "Apple Watch S9"]
        branches = ["CN_HN", "CN_HCM", "CN_DN"]
        
        curr_date = start_date
        records = []
        order_idx = 1
        
        while curr_date <= end_date:
            # 5 to 15 orders per day
            daily_orders = random.randint(5, 15)
            for _ in range(daily_orders):
                product = random.choice(products)
                branch = random.choice(branches)
                quantity = random.randint(1, 3)
                
                # Assign base price
                if product == "Iphone 15": price = 20000000
                elif product == "MacBook Pro M3": price = 40000000
                elif product == "AirPods Pro": price = 5000000
                elif product == "iPad Air": price = 15000000
                else: price = 10000000
                
                records.append(
                    NormalizedOrder(
                        order_id=f"ORD-{curr_date.strftime('%Y%m%d')}-{order_idx:04d}",
                        order_date=curr_date,
                        product_name=product,
                        quantity=quantity,
                        unit_price=price,
                        total_amount=quantity * price,
                        customer_name=f"Customer {random.randint(1, 100)}",
                        branch_id=branch,
                        source_sheet="seed_script"
                    )
                )
                order_idx += 1
            curr_date += timedelta(days=1)
            
        db.add_all(records)
        db.commit()
        print(f"Successfully seeded {len(records)} orders from {start_date} to {end_date}.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
