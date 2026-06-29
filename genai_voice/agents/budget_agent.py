"""budget_agent.py — the Budget checker (the fan-in / validation step).

After the four specialists finish (in parallel), the graph funnels into this one
agent. It adds up every cost and decides whether the plan fits. If it is over
budget — and we have not already retried too many times — it flags a re-plan,
which sends the team back to the supervisor to try cheaper options.

Notice this agent uses NO LLM: money math should be exact, so we use plain Python
(see tools/budget.py). Use the right tool for the job!
"""

from genai_voice.agents.base import note
from genai_voice.config import defaults
from genai_voice.tools.budget import format_money, is_within_budget, total_cost


def budget_node(state: dict) -> dict:
    # Add up the cost from each specialist's result.
    cost = total_cost(
        state.get("transport"),
        state.get("accommodation"),
        state.get("activities"),
        state.get("food"),
    )

    budget = state.get("budget", defaults.DEFAULT_BUDGET)
    within = is_within_budget(cost, budget)

    # Decide whether to loop back for a cheaper plan. The revisions counter caps
    # the loop so the graph can never run forever.
    revisions = state.get("revisions", 0)
    needs_revision = (not within) and (revisions < defaults.MAX_BUDGET_REVISIONS)

    verdict = "within budget" if within else "OVER budget"
    return {
        "running_cost": cost,
        "within_budget": within,
        "needs_revision": needs_revision,
        # Only count a revision when we are actually going to re-plan.
        "revisions": revisions + (1 if needs_revision else 0),
        "messages": note(
            "Budget agent",
            f"Total {format_money(cost)} vs budget {format_money(budget)} — {verdict}"
            + (" → re-planning cheaper" if needs_revision else ""),
        ),
    }


def budget_router(state: dict) -> str:
    """Decide where to go after the budget check.

    LangGraph calls this on the conditional edge out of the budget node. It must
    return one of the keys we map in build_graph.py: "replan" or "done".
    """
    return "replan" if state.get("needs_revision") else "done"
