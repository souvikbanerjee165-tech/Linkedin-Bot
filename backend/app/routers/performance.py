from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
from app import crud
from app.schemas import PerformanceLogResponse, PerformanceLogCreate, PerformanceAnalyticsSummary
from app.services.analytics_engine import analytics_engine
from app.services.prospect_evaluator import prospect_evaluator

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

# Inbound Pipeline & CRM
@router.get("/leads")
def get_leads():
    return crud.get_prospect_leads()

@router.post("/leads")
def create_lead(payload: Dict[str, Any] = Body(...)):
    created = crud.create_prospect_lead(payload)
    return created

@router.put("/leads/{lead_id}")
def update_lead(lead_id: int, payload: Dict[str, Any] = Body(...)):
    updated = crud.update_prospect_lead(lead_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Lead not found")
    return updated

@router.post("/leads/evaluate")
async def evaluate_and_add_lead(payload: Dict[str, Any] = Body(...)):
    target_url = payload.get("website_url")
    if not target_url:
        raise HTTPException(status_code=400, detail="website_url is required")

    try:
        result = await prospect_evaluator.inspect_and_evaluate(
            target_url=target_url,
            prospect_name=payload.get("prospect_name", "Prospective Client"),
            company=payload.get("company", ""),
            role_title=payload.get("role_title", "Business Leader"),
            product_focus=payload.get("product_focus", "dental_sales_intel")
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prospect evaluation error: {str(exc)}")
