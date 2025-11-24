from fastapi import APIRouter, Depends
from database import get_db
from utils.ingredient_normalizer import normalize_ingredient
from utils.ingredient_simplifier import simplify_ingredient
from utils.ingredient_nutrition import get_nutrition_for

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/nutrition")
def debug_nutrition(ingredient: str, db=Depends(get_db)):
    normalized = normalize_ingredient(ingredient)
    simplified = simplify_ingredient(ingredient)
    nutrition = get_nutrition_for(simplified, db)

    return {
        "raw": ingredient,
        "normalized": normalized,
        "simplified": simplified,
        "nutrition": nutrition
    }
