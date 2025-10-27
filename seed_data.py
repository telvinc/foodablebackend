from sqlalchemy.exc import IntegrityError
from database import Base, engine, SessionLocal
from models import GroceryItem, Recipe

Base.metadata.create_all(bind=engine)

db = SessionLocal()

groceries = [
    {"name": "Banana", "category": "Fruit", "calories": 89, "protein": 1.1},
    {"name": "Chicken Breast", "category": "Protein", "calories": 165, "protein": 31.0},
    {"name": "Brown Rice", "category": "Grain", "calories": 123, "protein": 2.6},
    {"name": "Broccoli", "category": "Vegetable", "calories": 55, "protein": 4.0},
    {"name": "Eggs", "category": "Protein", "calories": 155, "protein": 13.0},
]

recipes = [
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
    {
        "name": "Veggie Stir-Fry",
        "ingredients": "Broccoli,Carrots,Soy Sauce",
        "instructions": "Stir-fry veggies in a pan with soy sauce for 5-7 minutes.",
    },
]

def add_if_not_exists(model, unique_field, items):
    for item in items:
        existing = db.query(model).filter(getattr(model, unique_field) == item[unique_field]).first()
        if not existing:
            db.add(model(**item))
            print(f"Added {item[unique_field]}")
        else:
            print(f"Skipped duplicate: {item[unique_field]}")

try:
    add_if_not_exists(GroceryItem, "name", groceries)
    add_if_not_exists(Recipe, "name", recipes)
    db.commit()
except IntegrityError as e:
    db.rollback()
finally:
    db.close()
