"""activities.py — the Activities specialist agent.

This one uses TWO tools: the activities search AND the weather tool, so it can
prefer indoor plans when rain is likely. A nice example of an agent combining
multiple sources before deciding.
"""

from genai_voice.agents.base import ask_llm, note
from genai_voice.agents.prompts import ACTIVITIES_PROMPT
from genai_voice.tools.budget import format_money
from genai_voice.tools.weather import get_weather
from genai_voice.tools.web_search import search_activities


def activities_node(state: dict) -> dict:
    budget_friendly = state.get("needs_revision", False)
    preferences = state.get("preferences", [])

    data = search_activities(state["destination"], preferences, budget_friendly=budget_friendly)
    weather = get_weather(state["destination"])  # second tool

    recommendation = ask_llm(
        ACTIVITIES_PROMPT,
        f"Destination: {state['destination']}\n"
        f"Preferences: {preferences}\n"
        f"Activity ideas found by tool: {data['ideas']}\n"
        f"Weather: {weather['summary']} — {weather['advice']}",
    )

    return {
        "activities": {"summary": recommendation, "cost": data["cost"]},
        "messages": note("Activities agent", f"weather: {weather['summary']}, ~{format_money(data['cost'])}"),
    }
