from fastapi import APIRouter, HTTPException, status, Depends

from utils.ingredient_normalizer import normalize_ingredient
from utils.ingredient_matcher import match_ingredient
from utils.ingredient_nutrition import get_nutrition_for

from schemas import AISuggestionRequest, AISuggestionResponse
from ai_client import generate_ai_suggestions

from database import SessionLocal

router = APIRouter(prefix="/ai", tags=["ai"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/suggest", response_model=AISuggestionResponse)
def suggest_ai_ideas(payload: AISuggestionRequest, db=Depends(get_db)):
    if not payload.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must not be empty.",
        )

    ai_response = generate_ai_suggestions(payload)

    for item in ai_response.suggestions:
        normalized_list = [normalize_ingredient(i) for i in item.ingredients]

        # INTERNAL ONLY — do NOT expose to frontend
        internal_info = []

        for norm in normalized_list:
            nutrition = get_nutrition_for(norm, db)

            internal_info.append({
                "normalized": norm,
                "nutrition": nutrition
            })

        # store internally only
        item._internal_validation = internal_info

    return ai_response