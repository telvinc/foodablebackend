from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy import JSON
from database import Base

class GroceryItem(Base):
    __tablename__ = "groceries"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=True)
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    ingredients = Column(JSON, nullable=False)
    instructions = Column(Text, nullable=True)
