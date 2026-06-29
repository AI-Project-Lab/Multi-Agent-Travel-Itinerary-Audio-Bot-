"""state.py — the shared "memory" that flows through the agent graph.

In LangGraph every node (agent) receives the current STATE, does its job, and
returns a small dictionary of updates. LangGraph merges those updates back into
the state and passes it to the next node. So this file is the single source of
truth for "what information does the team pass around?".

Think of it like a shared travel notebook that each specialist writes a page in.
"""

from operator import add
from typing import Annotated, TypedDict


class ItineraryState(TypedDict, total=False):
    """All the fields the agents read from and write to.

    `total=False` means every field is optional — handy because the state is
    built up gradually (the supervisor fills some fields, specialists fill others).
    """

    # ---- Input -------------------------------------------------------------
    user_request: str          # the traveller's request, e.g. "2 day trip to Goa"

    # ---- Filled by the Supervisor agent (it parses the request) ------------
    destination: str
    days: int
    budget: float
    preferences: list          # e.g. ["beach", "vegetarian"]

    # ---- Filled by the specialist agents -----------------------------------
    # IMPORTANT: each of these keys is written by EXACTLY ONE agent. That is why
    # they do not need a special "reducer" — there is never a write conflict even
    # though the specialists run in parallel. Each dict holds a human summary plus
    # an estimated cost the Budget agent can add up.
    transport: dict
    accommodation: dict
    activities: dict
    food: dict

    # ---- Filled by the Budget agent ----------------------------------------
    running_cost: float        # sum of all specialist cost estimates
    within_budget: bool        # did we stay under the user's budget?
    revisions: int             # how many times we have re-planned for cost
    needs_revision: bool       # should the team try again with cheaper options?

    # ---- Filled by the Compiler agent --------------------------------------
    draft_itinerary: str       # the final day-by-day plan shown/spoken to the user

    # ---- Shared scratchpad -------------------------------------------------
    # Many agents append a short note here ("Transport agent: found 2 flights").
    # Because MULTIPLE nodes write to it at the same time, it needs a "reducer":
    # `Annotated[list, add]` tells LangGraph to MERGE the lists (add them) instead
    # of overwriting. This is the key trick that makes parallel agents safe.
    messages: Annotated[list, add]


def new_state(user_request: str) -> ItineraryState:
    """Create a fresh state for a brand-new request.

    Centralising this means we never forget to initialise a field.
    """
    return ItineraryState(
        user_request=user_request,
        preferences=[],
        revisions=0,
        needs_revision=False,
        messages=[],
    )
