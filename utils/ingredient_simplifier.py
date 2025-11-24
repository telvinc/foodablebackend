import re

UNITS = [
    "cup", "cups", "tbsp", "tablespoon", "tablespoons", "tsp", "teaspoon",
    "teaspoons", "gram", "grams", "g", "kg", "oz", "ounce", "ounces",
    "lb", "pound", "pounds", "ml", "l", "scoop", "scoops"
]

DESCRIPTORS = [
    "fresh", "grilled", "cooked", "raw", "large", "small", "chopped",
    "diced", "ground", "minced", "sliced", "ripe", "unsweetened"
]

def simplify_ingredient(raw: str) -> str:
    """
    A smarter ingredient simplifier:
    Keeps multi-word ingredients together
    Removes quantities + descriptors but preserves core food terms.
    """

    if not raw or not isinstance(raw, str):
        return ""

    text = raw.lower().strip()

    # Remove fractions and numbers
    text = re.sub(r"\b\d+\/\d+\b", "", text)
    text = re.sub(r"\b\d+(\.\d+)?\b", "", text)

    # Remove units
    unit_pattern = r"\b(" + "|".join(UNITS) + r")\b"
    text = re.sub(unit_pattern, "", text)

    # Remove descriptors
    desc_pattern = r"\b(" + "|".join(DESCRIPTORS) + r")\b"
    text = re.sub(desc_pattern, "", text)

    # Fix hyphens → replace with space instead of deleting
    text = text.replace("-", " ")

    # Remove stray punctuation, but keep spaces
    text = re.sub(r"[^a-zA-Z\s]", "", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text
