"""food.py — the Food specialist agent.

Finds places to eat and strictly respects dietary preferences (e.g. vegetarian).
Writes to the 'food' state key.
"""

from genai_voice.agents.base import ask_llm, note
from genai_voice.agents.prompts import FOOD_PROMPT
from genai_voice.tools.budget import format_money
from genai_voice.tools.web_search import search_restaurants


def food_node(state: dict) -> dict:
    budget_friendly = state.get("needs_revision", False)
    preferences = state.get("preferences", [])

    data = search_restaurants(state["destination"], preferences, budget_friendly=budget_friendly)

    recommendation = ask_llm(
        FOOD_PROMPT,
        f"Destination: {state['destination']}\n"
        f"Dietary preferences: {preferences}\n"
        f"Dining options found by tool: {data['spots']}\n"
        f"Estimated cost: {format_money(data['cost'])}",
    )

    return {
        "food": {"summary": recommendation, "cost": data["cost"]},
        "messages": note("Food agent", f"~{format_money(data['cost'])}"),
    }
