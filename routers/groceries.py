from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import GroceryItem
from schemas import Grocery, GroceryCreate
from auth import get_current_user
from models import User

router = APIRouter(prefix="/groceries", tags=["groceries"])

# ---------------------
# CREATE (user-specific)
# ---------------------
@router.post("/", response_model=Grocery, status_code=201)
def create_grocery(
    item: GroceryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_item = GroceryItem(
        name=item.name,
        category=item.category,
        calories=item.calories,
        protein=item.protein,
        user_id=current_user.id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# ---------------------
# LIST ONLY USER’S ITEMS
# ---------------------
@router.get("/", response_model=List[Grocery])
def list_groceries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(GroceryItem)
        .filter(GroceryItem.user_id == current_user.id)
        .all()
    )


# ---------------------
# GET ONE (must belong to user)
# ---------------------
@router.get("/{grocery_id}", response_model=Grocery)
def get_grocery(
    grocery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.get(GroceryItem, grocery_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Grocery item not found")
    return item


# ---------------------
# DELETE (must belong to user)
# ---------------------
@router.delete("/{grocery_id}", status_code=status.HTTP_200_OK)
def delete_grocery(
    grocery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.get(GroceryItem, grocery_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Grocery item not found")
    db.delete(item)
    db.commit()
    return {"detail": "Deleted"}


# ---------------------
# UPDATE (must belong to user)
# ---------------------
@router.put("/{grocery_id}", response_model=Grocery)
def update_grocery(
    grocery_id: int,
    payload: GroceryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.get(GroceryItem, grocery_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Grocery item not found")

    for k, v in payload.model_dump().items():
        setattr(item, k, v)

    db.commit()
    db.refresh(item)
    return item
