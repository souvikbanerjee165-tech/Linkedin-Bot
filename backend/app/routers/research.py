from fastapi import APIRouter, HTTPException
from typing import List
from app import crud
from app.schemas import ResearchItemResponse, ResearchItemCreate

router = APIRouter(prefix="/api/research", tags=["Research"])

@router.get("", response_model=List[ResearchItemResponse])
def get_research():
    return crud.get_research_items()

@router.post("", response_model=ResearchItemResponse)
def add_research_item(payload: ResearchItemCreate):
    created = crud.create_research_item(payload.model_dump())
    return created
