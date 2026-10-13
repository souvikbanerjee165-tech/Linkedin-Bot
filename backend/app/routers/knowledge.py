from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app import crud
from app.schemas import KnowledgeItemResponse, KnowledgeItemCreate, KnowledgeItemUpdate

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge"])

@router.get("", response_model=List[KnowledgeItemResponse])
def list_knowledge_items(category: Optional[str] = Query(None)):
    return crud.get_knowledge_items(category=category)

@router.post("", response_model=KnowledgeItemResponse)
def create_knowledge_item(payload: KnowledgeItemCreate):
    created = crud.create_knowledge_item(payload.model_dump())
    return created

@router.get("/{item_id}", response_model=KnowledgeItemResponse)
def get_knowledge_item(item_id: int):
    item = crud.get_knowledge_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    return item

@router.put("/{item_id}", response_model=KnowledgeItemResponse)
def update_knowledge_item(item_id: int, payload: KnowledgeItemUpdate):
    updated = crud.update_knowledge_item(item_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    return updated

@router.delete("/{item_id}")
def delete_knowledge_item(item_id: int):
    success = crud.delete_knowledge_item(item_id)
    return {"success": success, "deleted_id": item_id}
