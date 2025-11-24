from typing import Dict
from sqlalchemy.orm import Session

from utils.ingredient_matcher import match_ingredient
from usda_client import search_foods, pick_basic_macros


def get_nutrition_for(simplified_name: str, db: Session) -> Dict:
    if not simplified_name:
        return {"calories": None, "protein": None, "source": "none"}

    simplified = simplified_name.strip()
    if not simplified:
        return {"calories": None, "protein": None, "source": "none"}

    # 1. DB match
    match = match_ingredient(db, simplified)
    if match:
        return {
            "calories": match.calories,
            "protein": match.protein,
            "source": "db",
        }

    # 2. USDA fallback
    words = [w for w in simplified.split() if w]

    search_terms = [simplified]  # full phrase

    if len(words) >= 2:
        search_terms.append(" ".join(words[:2]))  # first two words

    search_terms.append(words[-1])  # last word

    # De-dupe
    seen = set()
    search_terms = [t for t in search_terms if not (t in seen or seen.add(t))]

    for term in search_terms:
        try:
            print("CALLING USDA →", term)
            results = search_foods(term)
            summary = pick_basic_macros(results)
            if summary:
                return {
                    "calories": summary["calories"],
                    "protein": summary["protein"],
                    "source": "usda",
                }
        except Exception as e:
            print("USDA ERROR:", e)

    return {"calories": None, "protein": None, "source": "none"}
