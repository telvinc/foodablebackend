import os
import json
from typing import List

from dotenv import load_dotenv
from openai import OpenAI

from schemas import (
    AISuggestionRequest,
    AISuggestedItem,
    AISuggestionResponse,
)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def build_prompt(payload: AISuggestionRequest) -> str:
    restrictions = ""
    if payload.dietary_restrictions:
        restrictions = (
            "The user has these dietary restrictions or preferences: "
            + ", ".join(payload.dietary_restrictions)
            + ". "
        )

    # SUPER-PROMPT with guaranteed full ingredient lists
    return (
        "You are an AI assistant that generates structured meal suggestions in JSON.\n"
        "Your job is to take the user query and return realistic, complete recipe ideas.\n"
        "Follow these strict rules:\n\n"

        "1. ALWAYS return JSON in exactly this structure:\n"
        "{\n"
        "  \"suggestions\": [\n"
        "    {\n"
        "      \"name\": \"\",\n"
        "      \"description\": \"\",\n"
        "      \"ingredients\": [],\n"
        "      \"estimated_cost\": 0,\n"
        "      \"calories\": 0,\n"
        "      \"protein\": 0\n"
        "    }\n"
        "  ]\n"
        "}\n\n"

        "2. INGREDIENT LIST RULES:\n"
        "- MUST include ALL ingredients needed to actually cook the recipe.\n"
        "- Include dry and wet ingredients.\n"
        "- Include common staples: eggs, butter, oil, sugar, salt, baking powder, vanilla, etc.\n"
        "- Minimum 5 ingredients unless the dish genuinely requires fewer.\n"
        "- EACH ingredient must be specific and measurable (e.g., \"2 tbsp butter\").\n\n"

        "3. NUTRITION:\n"
        "- Provide simple, realistic estimates.\n"
        "- Calories and protein should be approximate per-serving values.\n\n"

        "4. COST:\n"
        "- estimated_cost is the approximate cost of making the whole recipe.\n"
        "- Round to a simple number.\n\n"

        "5. RECIPE TYPE RULES:\n"
        "- If the query is dessert-related, ALL results must be desserts.\n"
        "- If the query names a food (e.g., brownies), ALL results must be variants of that food.\n"
        "- Respect dietary restrictions.\n"
        "- Never include commentary or extra fields.\n"
        "- Output ONLY raw JSON.\n\n"

        f"{restrictions}"
        f"Generate exactly {payload.max_results} recipe suggestions.\n"
        f"User query: \"{payload.query}\""
    )


def fake_suggestions(payload: AISuggestionRequest) -> AISuggestionResponse:
    items: List[AISuggestedItem] = [
        AISuggestedItem(
            name=f"Simple Protein Bowl #{i+1}",
            description="Chicken, rice, and veggies with a focus on protein and budget.",
            ingredients=["chicken breast", "brown rice", "broccoli", "olive oil"],
            estimated_cost=10.0 + i,
            calories=550 + i * 20,
            protein=40 + i * 3,
        )
        for i in range(min(payload.max_results, 3))
    ]
    return AISuggestionResponse(
        original_query=payload.query,
        suggestions=items,
    )


def generate_ai_suggestions(payload: AISuggestionRequest) -> AISuggestionResponse:
    if client is None or OPENAI_API_KEY.startswith("sk-your"):
        return fake_suggestions(payload)

    prompt = build_prompt(payload)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You output ONLY valid JSON. "
                        "Never include commentary. "
                        "Always produce complete ingredient lists."
                    )
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=700,
            temperature=0.4,
        )

        raw_output = response.choices[0].message.content

        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError:
            print("JSON PARSE ERROR — raw output:", raw_output)
            return fake_suggestions(payload)

        suggestions = []
        for item in parsed.get("suggestions", []):
            suggestions.append(
                AISuggestedItem(
                    name=item.get("name"),
                    description=item.get("description"),
                    ingredients=item.get("ingredients", []),
                    estimated_cost=item.get("estimated_cost"),
                    calories=item.get("calories"),
                    protein=item.get("protein"),
                )
            )

        return AISuggestionResponse(
            original_query=payload.query,
            suggestions=suggestions,
        )

    except Exception as e:
        print("AI ERROR:", e)
        return fake_suggestions(payload)
