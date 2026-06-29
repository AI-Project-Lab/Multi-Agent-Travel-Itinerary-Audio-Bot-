"""compiler.py — the Itinerary Writer (the final synthesis step).

Once the plan fits the budget, this agent gathers every specialist's piece and
asks the LLM to weave them into one warm, day-by-day itinerary that reads well
when spoken aloud. It also pulls in the brand "voice" from the data folder so the
tone stays on-brand.
"""

from genai_voice.agents.base import ask_llm, note
from genai_voice.agents.prompts import COMPILER_PROMPT
from genai_voice.config import defaults
from genai_voice.tools.budget import format_money


def _load_brand_context() -> str:
    """Read data/travel_bot_context.txt (tone/voice guidance), if it exists."""
    context_file = defaults.DATA_DIR / "travel_bot_context.txt"
    if context_file.exists():
        return context_file.read_text(encoding="utf-8")
    return ""


def compiler_node(state: dict) -> dict:
    brand_voice = _load_brand_context()

    # Pull each specialist's human summary (with a graceful fallback).
    def summary_of(key: str) -> str:
        return (state.get(key) or {}).get("summary", "(no suggestion)")

    user_content = (
        f"Destination: {state.get('destination')}\n"
        f"Number of days: {state.get('days')}\n"
        f"Budget: {format_money(state.get('budget', 0))}\n"
        f"Estimated total cost: {format_money(state.get('running_cost', 0))} "
        f"({'fits the budget' if state.get('within_budget') else 'slightly over budget'})\n\n"
        f"Transport: {summary_of('transport')}\n"
        f"Accommodation: {summary_of('accommodation')}\n"
        f"Activities: {summary_of('activities')}\n"
        f"Food: {summary_of('food')}\n"
    )

    # Append the brand voice to the compiler's role so tone stays consistent.
    system_prompt = COMPILER_PROMPT
    if brand_voice:
        system_prompt += f"\n\nBrand voice / context:\n{brand_voice}"

    itinerary = ask_llm(system_prompt, user_content)

    return {
        "draft_itinerary": itinerary,
        "messages": note("Compiler", "Final itinerary ready."),
    }
