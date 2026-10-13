from fastapi import APIRouter
from typing import List
from app import crud
from app.schemas import PerformanceLogResponse, PerformanceLogCreate, PerformanceAnalyticsSummary
from app.services.analytics_engine import analytics_engine

router = APIRouter(prefix="/api/performance", tags=["Performance"])

@router.get("", response_model=List[PerformanceLogResponse])
def get_performance_logs():
    return crud.get_performance_logs()

@router.post("", response_model=PerformanceLogResponse)
def log_performance(payload: PerformanceLogCreate):
    created = crud.log_post_performance(payload.model_dump())
    return created

@router.get("/summary", response_model=PerformanceAnalyticsSummary)
def get_analytics_summary():
    return analytics_engine.compute_summary()
