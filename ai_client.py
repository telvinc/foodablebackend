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

    return (
        "You are a recipe generator that ALWAYS matches the user's intent.\n"
        "RULES:\n"
        "- If the user asks for a dessert, return dessert recipes ONLY.\n"
        "- If the user mentions a specific food (e.g., brownies), ALL returned items MUST be variants of that food.\n"
        "- NEVER return savory meals unless the user explicitly asks.\n"
        "- ALWAYS respect the user's dietary preferences.\n"
        "- ALWAYS shape the output in the exact JSON structure below.\n\n"
        f"{restrictions}"
        f"Generate {payload.max_results} recipe ideas based strictly on the user's query.\n\n"
        "You MUST respond ONLY in this JSON format (no explanations):\n"
        "{\n"
        "  \"suggestions\": [\n"
        "    {\n"
        "      \"name\": \"string\",\n"
        "      \"description\": \"string\",\n"
        "      \"ingredients\": [\"string\", \"string\"],\n"
        "      \"estimated_cost\": float,\n"
        "      \"calories\": float,\n"
        "      \"protein\": float\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
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
                        "You output strictly valid JSON and ALWAYS match the user's recipe domain. "
                        "Desserts must return desserts, savory stays savory."
                    )
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
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
