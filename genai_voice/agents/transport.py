"""transport.py — the Transport specialist agent.

Pattern shared by all four specialists:
  1. call its OWN tool to fetch real-ish data (here: search_transport),
  2. ask the LLM to turn that data into a friendly recommendation,
  3. write its result to its OWN state key ('transport') so the parallel agents
     never overwrite each other.
"""

from genai_voice.agents.base import ask_llm, note
from genai_voice.agents.prompts import TRANSPORT_PROMPT
from genai_voice.tools.budget import format_money
from genai_voice.tools.web_search import search_transport


def transport_node(state: dict) -> dict:
    # needs_revision is True only when the Budget agent sent us back to find
    # cheaper options — the tool then returns budget-friendly choices.
    budget_friendly = state.get("needs_revision", False)

    data = search_transport(state["destination"], budget_friendly=budget_friendly)

    recommendation = ask_llm(
        TRANSPORT_PROMPT,
        f"Destination: {state['destination']}\n"
        f"Days: {state.get('days')}\n"
        f"Options found by tool: {data['summary']}\n"
        f"Estimated cost: {format_money(data['cost'])}",
    )

    return {
        "transport": {"summary": recommendation, "cost": data["cost"]},
        "messages": note("Transport agent", f"~{format_money(data['cost'])}"),
    }
