from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Data Sync & Report Automation API",
    description="Backend API cho đồ án tự động hóa báo cáo và đồng bộ dữ liệu.",
    version="1.0.0",
)

# Cấu hình CORS để cho phép Desktop App và Android App truy cập
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong thực tế nên giới hạn các domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to Data Sync & Report Automation API"}

# Router sẽ được include ở đây sau khi tạo api_router
from app.api.v1.api_router import api_router
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
def startup_event():
    from app.db.database import engine, Base
    import app.db.models
    Base.metadata.create_all(bind=engine)
    from app.services.scheduler_service import start_scheduler
    start_scheduler()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
