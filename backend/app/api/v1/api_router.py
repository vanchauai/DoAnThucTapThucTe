from fastapi import APIRouter
from .endpoints import auth, users, data_sources, reports, scheduler, insights

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(data_sources.router, prefix="/data-sources", tags=["data-sources"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(scheduler.router, prefix="/scheduler", tags=["scheduler"])
api_router.include_router(insights.router, prefix="/insights", tags=["insights"])
