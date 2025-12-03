from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel


# ======================
# Existing Schemas
# ======================

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


# ======================
# New: Auth / User Schemas
# ======================

class UserBase(BaseModel):
    email: str
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserPublic(UserBase):
    id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ======================
# New: Community / Posts / Comments
# ======================

class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    user: UserPublic
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PostBase(BaseModel):
    content: str
    # matches frontend idea of "recipe" | "grocery" | "text"
    type: Optional[str] = "text"


class PostCreate(PostBase):
    pass


class Post(BaseModel):
    id: int
    content: str
    type: Optional[str] = "text"
    user: UserPublic
    likes_count: int
    comments_count: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PostDetail(Post):
    comments: List[Comment] = []


class UserStats(BaseModel):
    total_posts: int
    total_comments: int
    total_likes_received: int


class UserProfile(BaseModel):
    user: UserPublic
    posts: List[Post]
    stats: UserStats

class SavedRecipeBase(BaseModel):
    recipe_id: int

class SavedRecipeResponse(BaseModel):
    id: int
    recipe_id: int
    created_at: datetime  

    class Config:
        from_attributes = True