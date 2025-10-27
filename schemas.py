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
