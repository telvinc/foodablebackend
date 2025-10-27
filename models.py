from sqlalchemy import Column, Integer, String, Float
from database import Base

class GroceryItem(Base):
    __tablename__ = "groceries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=True)
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    ingredients = Column(String, nullable=False)
    instructions = Column(String, nullable=True)
