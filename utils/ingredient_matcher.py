from sqlalchemy.orm import Session
from models import GroceryItem

def match_ingredient(db: Session, simplified: str):
    if not simplified:
        return None

    # 1. Exact match
    exact = db.query(GroceryItem).filter(
        GroceryItem.name.ilike(simplified)
    ).first()
    if exact:
        return exact

    # 2. Contains (partial)
    partial = db.query(GroceryItem).filter(
        GroceryItem.name.ilike(f"%{simplified}%")
    ).first()
    if partial:
        return partial

    # 3. Word-by-word match (e.g., "cocoa powder" → matches "unsweetened cocoa powder")
    words = simplified.split()
    if len(words) > 1:
        q = db.query(GroceryItem)
        for w in words:
            q = q.filter(GroceryItem.name.ilike(f"%{w}%"))
        deep_match = q.first()
        if deep_match:
            return deep_match

    return None
