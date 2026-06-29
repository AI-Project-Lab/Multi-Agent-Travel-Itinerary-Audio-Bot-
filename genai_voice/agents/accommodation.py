"""accommodation.py — the Accommodation specialist agent.

Same three-step pattern as transport.py, but its tool finds places to stay and it
writes to the 'accommodation' state key.
"""

from genai_voice.agents.base import ask_llm, note
from genai_voice.agents.prompts import ACCOMMODATION_PROMPT
from genai_voice.tools.budget import format_money
from genai_voice.tools.web_search import search_accommodation


def accommodation_node(state: dict) -> dict:
    budget_friendly = state.get("needs_revision", False)

    data = search_accommodation(state["destination"], budget_friendly=budget_friendly)

    recommendation = ask_llm(
        ACCOMMODATION_PROMPT,
        f"Destination: {state['destination']}\n"
        f"Stay options found by tool: {data['options']}\n"
        f"Suggested pick: {data['summary']}\n"
        f"Estimated cost: {format_money(data['cost'])}",
    )

    return {
        "accommodation": {"summary": recommendation, "cost": data["cost"]},
        "messages": note("Accommodation agent", f"~{format_money(data['cost'])}"),
    }
