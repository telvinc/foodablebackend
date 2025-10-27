import os, requests
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("USDA_API_KEY")

def search_foods(query: str, page_size: int = 5):
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {"api_key": API_KEY, "query": query, "pageSize": page_size}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def pick_basic_macros(food_json):
    """Return calories and protein if present, else None."""
    foods = food_json.get("foods", [])
    if not foods:
        return None
    top = foods[0]  # just take the first match for PR1
    kcals = None
    protein = None
    for n in top.get("foodNutrients", []):
        name = (n.get("nutrientName") or "").lower()
        if "energy" in name and ("kcal" in (n.get("unitName") or "").lower()):
            kcals = n.get("value")
        if name == "protein":
            protein = n.get("value")
    return {"description": top.get("description"), "calories": kcals, "protein": protein}
    
if __name__ == "__main__":
    data = search_foods("banana")
    summary = pick_basic_macros(data)
    print(summary)
