"""supervisor.py — the ROUTER / coordinator of the team.

The supervisor is the heart of "multi-agent orchestration". Its job here is to:
  1. read the traveller's free-text request,
  2. extract structured trip details (destination, days, budget, preferences),
  3. hand those details to the specialists.

We use the LLM's "structured output" feature: instead of free text, we ask the
model to fill in a typed form (the TripBrief below). That makes the result safe
to use in code.
"""

from pydantic import BaseModel, Field

from genai_voice.agents.base import note
from genai_voice.agents.prompts import SUPERVISOR_PROMPT
from genai_voice.config import defaults
from genai_voice.models.llm import get_llm
from genai_voice.tools.budget import format_money


class TripBrief(BaseModel):
    """The structured form the supervisor fills in from the request.

    Defaults let the model leave a field blank when the user did not mention it;
    we then substitute the project defaults below.
    """

    destination: str = Field(default="", description="City or place to visit")
    days: int = Field(default=0, description="Number of days for the trip")
    budget: float = Field(default=0, description="Total budget as a number")
    preferences: list[str] = Field(
        default_factory=list,
        description='Short keywords e.g. ["beach", "vegetarian"]',
    )


def supervisor_node(state: dict) -> dict:
    """Parse the request the first time; coordinate a cheaper re-plan after that."""

    # If we already parsed the trip (we are looping back to cut costs), don't
    # waste another LLM call — just announce the re-plan. The specialists will
    # see needs_revision=True and switch to budget-friendly options.
    if state.get("destination"):
        return {"messages": note("Supervisor", "Over budget — re-planning with cheaper options.")}

    # Ask the LLM to fill in the TripBrief form from the free-text request.
    extractor = get_llm().with_structured_output(TripBrief)
    brief: TripBrief = extractor.invoke(
        f"{SUPERVISOR_PROMPT}\n\nTraveller request:\n{state['user_request']}"
    )

    # Apply sensible defaults wherever the traveller didn't say.
    destination = brief.destination.strip() or "your destination"
    days = brief.days or defaults.DEFAULT_DAYS
    budget = brief.budget or defaults.DEFAULT_BUDGET

    return {
        "destination": destination,
        "days": days,
        "budget": budget,
        "preferences": brief.preferences,
        "messages": note(
            "Supervisor",
            f"Planning a {days}-day trip to {destination} "
            f"(budget {format_money(budget)}, likes: {', '.join(brief.preferences) or 'none stated'}).",
        ),
    }
