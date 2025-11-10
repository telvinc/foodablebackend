from sqlalchemy.orm import Session
from models import GroceryItem, Recipe

GROCERIES = [
    {"name": "Banana", "category": "Fruit", "calories": 89, "protein": 1.1},
    {"name": "Chicken Breast", "category": "Protein", "calories": 165, "protein": 31.0},
    {"name": "Brown Rice", "category": "Grain", "calories": 123, "protein": 2.6},
    {"name": "Broccoli", "category": "Vegetable", "calories": 55, "protein": 4.0},
    {"name": "Eggs", "category": "Protein", "calories": 155, "protein": 13.0},
]

RECIPES = [
    {
        "name": "Chicken and Rice Bowl",
        "ingredients": "Chicken Breast,Brown Rice,Broccoli",
        "instructions": "Cook chicken and rice separately, steam broccoli, then combine in a bowl.",
    },
    {
        "name": "Banana Smoothie",
        "ingredients": "Banana,Milk,Yogurt",
        "instructions": "Blend banana, milk, and yogurt until smooth.",
    },
]

def seed_groceries(db: Session) -> None:
    """Seed groceries if the table is empty."""
    if db.query(GroceryItem).count() > 0:
        return
    db.add_all([GroceryItem(**g) for g in GROCERIES])
    db.commit()

def seed_recipes(db: Session) -> None:
    """Seed recipes if the table is empty."""
    if db.query(Recipe).count() > 0:
        return
    db.add_all([Recipe(**r) for r in RECIPES])
    db.commit()
