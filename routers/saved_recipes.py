from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user
from models import SavedRecipe, Recipe, User
from schemas import SavedRecipeBase, SavedRecipeResponse

router = APIRouter(prefix="/saved-recipes", tags=["saved-recipes"])


# Save a recipe
@router.post("/", response_model=SavedRecipeResponse)
def save_recipe(
    payload: SavedRecipeBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate recipe exists
    recipe = db.get(Recipe, payload.recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Check if already saved
    existing = (
        db.query(SavedRecipe)
        .filter(
            SavedRecipe.user_id == current_user.id,
            SavedRecipe.recipe_id == payload.recipe_id,
        )
        .first()
    )
    if existing:
        return existing

    saved = SavedRecipe(
        user_id=current_user.id,
        recipe_id=payload.recipe_id,
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


# Remove saved recipe
@router.delete("/{recipe_id}")
def unsave_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(SavedRecipe)
        .filter(
            SavedRecipe.user_id == current_user.id,
            SavedRecipe.recipe_id == recipe_id,
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Not saved")

    db.delete(item)
    db.commit()
    return {"detail": "removed"}


# List user’s saved recipes
@router.get("/", response_model=list[SavedRecipeResponse])
def list_saved(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = (
        db.query(SavedRecipe)
        .filter(SavedRecipe.user_id == current_user.id)
        .all()
    )
    return items
