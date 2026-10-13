from fastapi import APIRouter, HTTPException
from typing import List
from app import crud
from app.schemas import ProductResponse, ProductUpdate

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("", response_model=List[ProductResponse])
def list_products():
    return crud.get_products()

@router.get("/{product_key}", response_model=ProductResponse)
def get_product(product_key: str):
    product = crud.get_product_by_key(product_key)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_key}", response_model=ProductResponse)
def update_product(product_key: str, payload: ProductUpdate):
    updated = crud.update_product(product_key, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated
