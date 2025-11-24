import re

UNITS = [
    "cup", "cups", "tbsp", "tablespoon", "tablespoons", "tsp", "teaspoon",
    "teaspoons", "gram", "grams", "g", "kg", "oz", "ounce", "ounces",
    "lb", "pound", "pounds", "ml", "l"
]

DESCRIPTORS = [
    "fresh", "grilled", "cooked", "raw", "large", "small", "chopped",
    "diced", "ground", "minced", "sliced"
]

def normalize_ingredient(raw: str) -> str:
    if not raw or not isinstance(raw, str):
        return ""

    text = raw.lower().strip()

    text = re.sub(r"\b\d+\/\d+\b", "", text)   # fractions like 1/2
    text = re.sub(r"\b\d+(\.\d+)?\b", "", text)  # numbers like 2 or 2.5

    unit_pattern = r"\b(" + "|".join(UNITS) + r")\b"
    text = re.sub(unit_pattern, "", text)

    desc_pattern = r"\b(" + "|".join(DESCRIPTORS) + r")\b"
    text = re.sub(desc_pattern, "", text)

    text = re.sub(r"[^a-zA-Z\s]", "", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text
