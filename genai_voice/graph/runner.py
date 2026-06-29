"""runner.py — the simple front door to the whole agent team.

Everything else (Gradio app, CLI) calls `run_itinerary()` here so they never have
to know about LangGraph internals. This is a "facade": one easy function hiding a
more complex system behind it.
"""

import uuid

from genai_voice.graph.build_graph import get_graph
from genai_voice.state import new_state
from genai_voice.tools.budget import format_money


def run_itinerary(user_request: str, history: str = "") -> dict:
    """Plan a trip from a free-text (or transcribed) request.

    Args:
        user_request: what the traveller asked for, e.g. "2 day trip to Goa".
        history: optional text of the earlier conversation, so follow-up questions
                 ("suggest vegetarian restaurants") keep context. We simply prepend
                 it to the request — an easy, reliable form of memory.

    Returns:
        A dict with the final itinerary plus some "behind the scenes" details that
        are great for teaching (the running cost and each agent's notes).
    """
    graph = get_graph()

    # If we have earlier context, give it to the team alongside the new request.
    full_request = user_request
    if history:
        full_request = f"Earlier conversation:\n{history}\n\nNew request:\n{user_request}"

    # A checkpointer needs a thread_id. We use a fresh id per request so each plan
    # starts clean (no leftover destination from a previous trip). recursion_limit
    # is a safety cap on how many steps the graph may take.
    config = {
        "configurable": {"thread_id": str(uuid.uuid4())},
        "recursion_limit": 50,
    }

    final_state = graph.invoke(new_state(full_request), config)

    return {
        "itinerary": final_state.get("draft_itinerary", "Sorry, I could not build a plan."),
        "destination": final_state.get("destination", ""),
        "running_cost": final_state.get("running_cost", 0),
        "within_budget": final_state.get("within_budget", True),
        # The scratchpad notes — show these in the UI to reveal how the team worked.
        "trace": final_state.get("messages", []),
    }


def run_cli() -> None:
    """Tiny terminal demo so you can test the agents without the microphone/UI.

    Run it with:  poetry run RunItineraryGraph
    """
    import sys

    # Use a command-line request if given, otherwise a friendly default.
    request = " ".join(sys.argv[1:]) or "Plan a 2-day trip to Goa with beach activities"

    print(f"\nRequest: {request}\n" + "-" * 60)
    result = run_itinerary(request)

    print("\nAGENT TRACE (what each team member did):")
    for line in result["trace"]:
        print("  " + line)

    print("\n" + "=" * 60)
    print(result["itinerary"])
    print("=" * 60)
    print(f"\nEstimated total: {format_money(result['running_cost'])} "
          f"({'within budget' if result['within_budget'] else 'over budget'})\n")
