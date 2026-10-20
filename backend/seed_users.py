import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models.user import User
from app.core.security import get_password_hash

def seed_users():
    db = SessionLocal()
    try:
        from app.db.models.report import Report
        # Clear existing users and reports
        print("Clearing old reports and users...")
        db.query(Report).delete()
        db.query(User).delete()
        db.commit()

        pwd = get_password_hash("Admin@123")

        users_to_create = [
            # Admin
            User(email="admin@company.com", hashed_password=pwd, full_name="System Admin", role="admin", branch_id="ALL", is_active=True),
            
            # CN_HN
            User(email="manager.hn@company.com", hashed_password=pwd, full_name="Manager HN", role="manager", branch_id="CN_HN", is_active=True),
            User(email="nv.hn@company.com", hashed_password=pwd, full_name="Nhan vien HN", role="employee", branch_id="CN_HN", is_active=True),
            
            # CN_HCM
            User(email="manager.hcm@company.com", hashed_password=pwd, full_name="Manager HCM", role="manager", branch_id="CN_HCM", is_active=True),
            User(email="nv.hcm@company.com", hashed_password=pwd, full_name="Nhan vien HCM", role="employee", branch_id="CN_HCM", is_active=True),
            
            # CN_DN
            User(email="manager.dn@company.com", hashed_password=pwd, full_name="Manager DN", role="manager", branch_id="CN_DN", is_active=True),
            User(email="nv.dn@company.com", hashed_password=pwd, full_name="Nhan vien DN", role="employee", branch_id="CN_DN", is_active=True),
        ]

        db.add_all(users_to_create)
        db.commit()
        
        print("\nSuccessfully seeded users. Credentials:")
        print("Mật khẩu chung cho tất cả: Admin@123")
        print("-" * 50)
        for u in users_to_create:
            print(f"Email: {u.email:<25} | Role: {u.role:<8} | Branch: {u.branch_id}")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
