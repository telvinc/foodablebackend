from typing import List, Optional
from pydantic import BaseModel

class GroceryBase(BaseModel):
    name: str
    category: str | None = None
    calories: float | None = None
    protein: float | None = None

class GroceryCreate(GroceryBase):
    pass

class Grocery(GroceryBase):
    id: int

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    name: str
    ingredients: List[str]
    instructions: Optional[str] = None

class RecipeCreate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: int

    class Config:
        from_attributes = True

class AISuggestionRequest(BaseModel):
    query: str
    dietary_restrictions: Optional[List[str]] = None
    max_results: int = 5


class AISuggestedItem(BaseModel):
    name: str
    description: Optional[str] = None
    ingredients: List[str] = []
    estimated_cost: Optional[float] = None
    calories: Optional[float] = None
    protein: Optional[float] = None


class AISuggestionResponse(BaseModel):
    original_query: str
    suggestions: List[AISuggestedItem]

    class Config:
        from_attributes = True
