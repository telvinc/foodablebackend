from fastapi import APIRouter, HTTPException, status

from schemas import (
    AISuggestionRequest,
    AISuggestionResponse,
)
from ai_client import generate_ai_suggestions

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/suggest", response_model=AISuggestionResponse, status_code=status.HTTP_200_OK)
def suggest_ai_ideas(payload: AISuggestionRequest):
    if not payload.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must not be empty.",
        )

    return generate_ai_suggestions(payload)
