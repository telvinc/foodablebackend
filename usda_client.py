import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("USDA_API_KEY") or os.getenv("FDC_API_KEY")


def _clean_query(query: str) -> str:
    """Normalize search text and strip stray quotes we were passing before."""
    if not query:
        return ""
    q = query.strip()
    if q.startswith('"') and q.endswith('"') and len(q) > 2:
        q = q[1:-1].strip()
    return q


def search_foods(query: str, page_size: int = 5):
    """
    Call USDA FoodData Central /v1/foods/search.

    Uses POST with a JSON body (matches current API docs).
    Raises if the API returns a non-2xx status.
    """
    q = _clean_query(query)
    if not q:
        return {"foods": []}

    if not API_KEY:
        raise RuntimeError(
            "USDA_API_KEY (or FDC_API_KEY) is not set in the environment."
        )

    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {"api_key": API_KEY}
    payload = {"query": q, "pageSize": page_size}

    resp = requests.post(url, params=params, json=payload, timeout=20)
    resp.raise_for_status()
    return resp.json()


def pick_basic_macros(food_json):
    """
    Given the JSON from /foods/search, return a simple summary:

        {
            "description": str,
            "calories": float | None,
            "protein": float | None,
        }

    or None if we can't find useful nutrients.
    """
    if not isinstance(food_json, dict):
        return None

    foods = food_json.get("foods") or []
    if not foods:
        return None

    # Prefer more stable data types if available
    priority = {
        "Foundation": 4,
        "SR Legacy": 3,
        "Survey (FNDDS)": 2,
        "Branded": 1,
    }

    def score(food):
        return priority.get(food.get("dataType"), 0)

    top = max(foods, key=score)

    kcals = None
    protein = None

    for n in top.get("foodNutrients", []):
        name = (n.get("nutrientName") or "").lower()
        unit = (n.get("unitName") or "").lower()
        value = n.get("value")

        if value is None:
            continue

        # Energy
        if "energy" in name:
            if unit == "kcal":
                kcals = float(value)
            elif unit == "kj":
                kcals = float(value) / 4.184

        # Protein
        if "protein" in name and unit == "g":
            protein = float(value)

    if kcals is None and protein is None:
        return None

    return {
        "description": top.get("description"),
        "calories": kcals,
        "protein": protein,
    }


if __name__ == "__main__":
    data = search_foods("banana")
    summary = pick_basic_macros(data)
    print(summary)
