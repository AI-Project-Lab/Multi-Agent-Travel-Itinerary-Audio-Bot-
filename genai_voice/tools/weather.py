"""weather.py — a small weather tool used by the Activities agent.

Why a weather tool? So the Activities agent can prefer indoor plans on rainy
days — a simple, concrete example of an agent using a tool to make a better
decision.

REAL VERSION: call a free weather API (e.g. open-meteo.com or OpenWeatherMap)
using `requests`. Here we return a deterministic sample forecast so the class
project runs without another API key.
"""


def get_weather(destination: str) -> dict:
    """Return a (sample) short-range forecast for the destination."""
    # Deterministic 'forecast' so demos are repeatable: pick by name length.
    # Replace this whole block with a real API call when you are ready.
    name = (destination or "").strip().lower()
    rainy = name.endswith(("a", "i"))  # purely illustrative rule for the demo

    if rainy:
        return {
            "summary": "Cloudy with a chance of rain",
            "is_rainy": True,
            "advice": "Keep a couple of indoor options (museums, cafes) as backup.",
        }
    return {
        "summary": "Mostly sunny and pleasant",
        "is_rainy": False,
        "advice": "Great for outdoor sightseeing and beaches.",
    }
