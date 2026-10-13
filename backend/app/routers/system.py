from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
from app.config import settings
from app import crud
from app.database import create_database_backup, restore_database_backup
from app.schemas import ApiUsageSummary

router = APIRouter(prefix="/api/system", tags=["System"])

@router.get("/status", response_model=ApiUsageSummary)
def get_system_status():
    summary = crud.get_api_usage_summary()
    return ApiUsageSummary(
        total_calls=summary.get("total_calls", 0),
        total_prompt_tokens=summary.get("total_prompt_tokens", 0),
        total_completion_tokens=summary.get("total_completion_tokens", 0),
        total_tokens=summary.get("total_tokens", 0),
        total_cost_usd=round(summary.get("total_cost_usd", 0.0), 5),
        is_api_key_configured=settings.is_api_key_configured,
        current_model=settings.deepseek_model
    )

@router.post("/backup")
def create_backup():
    try:
        backup_path = create_database_backup()
        return {"success": True, "backup_path": backup_path}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/restore")
def restore_backup(backup_path: str = Query(...)):
    try:
        success = restore_database_backup(backup_path)
        return {"success": success, "restored_from": backup_path}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
