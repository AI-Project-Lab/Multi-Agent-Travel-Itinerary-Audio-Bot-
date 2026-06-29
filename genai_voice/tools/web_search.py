"""web_search.py — the 'lookup' tools used by the four specialist agents.

In a production bot these functions would call a real source (Playwright scraping
a travel site, a flights API, a hotels API, etc.). For a beginner-friendly,
always-runnable class project they return curated SAMPLE data that still feels
real and, importantly, includes a COST estimate so the Budget agent has numbers
to add up.

The `budget_friendly` flag lets the team re-plan with cheaper options when the
first plan is over budget — that is how the budget loop in the graph works.
"""

# A tiny "knowledge base" so popular destinations feel specific. Anything not
# listed falls back to generic-but-sensible options.
_KNOWN = {
    "goa": {
        "transport": "Direct flight + airport taxi; scooter rental on arrival",
        "hotels": ["Beachside resort in North Goa", "Budget guesthouse in Anjuna"],
        "activities": ["Beach hopping (Baga, Anjuna)", "Sunset cruise", "Old Goa churches"],
        "food": ["Goan fish curry shacks", "Beachfront cafes", "Vegetarian thali spots"],
    },
    "jaipur": {
        "transport": "Overnight train or short flight; auto-rickshaws in city",
        "hotels": ["Heritage haveli stay", "Budget hostel near City Palace"],
        "activities": ["Amber Fort", "Hawa Mahal", "Local bazaar shopping"],
        "food": ["Rajasthani thali", "Street chaat at MI Road", "Pure-veg restaurants"],
    },
}


def _lookup(destination: str):
    """Return the sample record for a destination (case-insensitive), or {}."""
    return _KNOWN.get((destination or "").strip().lower(), {})


def search_transport(destination: str, budget_friendly: bool = False) -> dict:
    """Find how to get there and get around.

    REAL VERSION: scrape a flights/trains site with Playwright, or call an API.
    """
    data = _lookup(destination)
    option = data.get("transport", f"Flight or train to {destination}, local cabs to get around")
    # Cheaper option when re-planning for budget.
    if budget_friendly:
        option = f"Budget bus/train to {destination}, shared autos locally"
        cost = 3500
    else:
        cost = 7000
    return {"summary": option, "cost": cost}


def search_accommodation(destination: str, budget_friendly: bool = False) -> dict:
    """Find a place to stay.

    REAL VERSION: query a hotels API (Booking/Agoda) or scrape listings.
    """
    data = _lookup(destination)
    hotels = data.get("hotels", [f"Mid-range hotel in {destination}", f"Budget stay in {destination}"])
    # hotels[0] is the nicer pick, hotels[-1] is the cheaper pick.
    pick = hotels[-1] if budget_friendly else hotels[0]
    cost = 2500 if budget_friendly else 6000
    return {"summary": pick, "options": hotels, "cost": cost}


def search_activities(destination: str, preferences=None, budget_friendly: bool = False) -> dict:
    """Find things to do, biased toward the traveller's preferences.

    REAL VERSION: scrape an attractions/tours site or call a places API.
    """
    preferences = preferences or []
    data = _lookup(destination)
    ideas = data.get("activities", [f"Top sights of {destination}", "Local walking tour", "Markets"])
    # If the user mentioned a preference (e.g. "beach"), surface it first.
    pref_note = f" (focused on: {', '.join(preferences)})" if preferences else ""
    cost = 1500 if budget_friendly else 3000
    return {"summary": f"{', '.join(ideas)}{pref_note}", "ideas": ideas, "cost": cost}


def search_restaurants(destination: str, preferences=None, budget_friendly: bool = False) -> dict:
    """Find places to eat, respecting dietary preferences (e.g. vegetarian).

    REAL VERSION: scrape a reviews site (Zomato/Yelp) or call a places API.
    """
    preferences = preferences or []
    data = _lookup(destination)
    spots = data.get("food", [f"Popular local eateries in {destination}", "Cafes", "Street food"])
    diet = "vegetarian" if any("veg" in p.lower() for p in preferences) else "mixed"
    cost = 1200 if budget_friendly else 2500
    return {"summary": f"{', '.join(spots)} — {diet} options available", "spots": spots, "cost": cost}
