# routers/recipes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Recipe
from schemas import Recipe as RecipeSchema, RecipeCreate

import json

router = APIRouter(prefix="/recipes", tags=["recipes"])

def _to_list(ingredients):
    """Normalize DB value to List[str]. Accepts list, JSON string, or comma string."""
    if isinstance(ingredients, list):
        return ingredients
    if not ingredients:
        return []
    s = ingredients.strip()
    # try JSON first: '["a","b"]'
    if s.startswith("["):
        try:
            val = json.loads(s)
            if isinstance(val, list):
                return [str(x) for x in val]
        except Exception:
            pass
    # fallback: 'a,b,c'
    return [p.strip() for p in s.split(",") if p.strip()]

def _to_db_value(ingredients: List[str]) -> str:
    """Store as a simple comma-separated string to match your current model."""
    return ",".join(ingredients)

@router.get("/", response_model=List[RecipeSchema])
def list_recipes(db: Session = Depends(get_db)):
    rows = db.query(Recipe).order_by(Recipe.id.desc()).all()
    for r in rows:
        r.ingredients = _to_list(r.ingredients)
    return rows

@router.get("/{recipe_id}", response_model=RecipeSchema)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    rec = db.get(Recipe, recipe_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recipe not found")
    rec.ingredients = _to_list(rec.ingredients)
    return rec

@router.post("/", response_model=RecipeSchema, status_code=status.HTTP_201_CREATED)
def create_recipe(payload: RecipeCreate, db: Session = Depends(get_db)):
    rec = Recipe(
        name=payload.name,
        ingredients=_to_db_value(payload.ingredients),  # store as string
        instructions=payload.instructions,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    # return with list so it matches the schema
    rec.ingredients = payload.ingredients
    return rec
