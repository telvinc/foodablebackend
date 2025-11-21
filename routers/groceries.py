from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import GroceryItem
from schemas import Grocery, GroceryCreate

router = APIRouter(prefix="/groceries", tags=["groceries"])

@router.post("/", response_model=Grocery, status_code=201)
def create_grocery(item: GroceryCreate, db: Session = Depends(get_db)):
    db_item = GroceryItem(
        name=item.name,
        category=item.category,
        calories=item.calories,
        protein=item.protein
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/", response_model=List[Grocery])
def list_groceries(db: Session = Depends(get_db)):
    return db.query(GroceryItem).all()

@router.get("/{grocery_id}", response_model=Grocery)
def get_grocery(grocery_id: int, db: Session = Depends(get_db)):
    item = db.query(GroceryItem).get(grocery_id)
    if not item:
        raise HTTPException(status_code=404, detail="Grocery item not found")
    return item

@router.delete("/{grocery_id}", status_code=status.HTTP_200_OK)
def delete_grocery(grocery_id: int, db: Session = Depends(get_db)):
    item = db.get(GroceryItem, grocery_id)
    if not item:
        raise HTTPException(status_code=404, detail="Grocery item not found")
    db.delete(item)
    db.commit()
    return {"detail": "Deleted"}

@router.put("/{grocery_id}", response_model=Grocery)
def update_grocery(grocery_id: int, payload: GroceryCreate, db: Session = Depends(get_db)):
    item = db.get(GroceryItem, grocery_id)
    if not item:
        raise HTTPException(status_code=404, detail="Grocery item not found")
    for k, v in payload.model_dump().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


