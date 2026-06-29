"""budget.py — plain, deterministic money math for the Budget agent.

Important teaching point: not everything should be done by the LLM! Adding up
costs is exact arithmetic, so we use ordinary Python here. Agents should reach
for real tools/code when precision matters, and use the LLM for language and
judgement.
"""

from genai_voice.config import defaults


def total_cost(*parts: dict) -> float:
    """Add up the 'cost' field from each specialist's result dict.

    Each `part` looks like {"summary": "...", "cost": 6000}. Missing costs count
    as 0 so a half-filled plan never crashes the math.
    """
    return float(sum((p or {}).get("cost", 0) for p in parts))


def is_within_budget(running_cost: float, budget: float) -> bool:
    """True when the plan's total is at or under the traveller's budget."""
    return running_cost <= budget


def format_money(amount: float) -> str:
    """Pretty-print an amount with the configured currency, e.g. 'INR 12,500'."""
    return f"{defaults.DEFAULT_CURRENCY} {amount:,.0f}"
