"""defaults.py — all the knobs for the project live here in ONE place.

Keeping settings centralised means a beginner can tweak behaviour (which model,
how many budget retries, where the data folder is) without hunting through the code.
"""

import os
from pathlib import Path

from dotenv import load_dotenv  # reads key=value pairs from the .env file

# Load the .env file (if present) so os.getenv() can see OPENAI_API_KEY etc.
# This is safe to call multiple times.
load_dotenv()

# --- Project paths ---------------------------------------------------------
# PROJECT_ROOT points at the top folder (the one holding pyproject.toml).
# We compute it relative to THIS file so it works on any machine.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

# --- LLM (large language model) settings -----------------------------------
# The API key is read from the environment. We do NOT hard-code it.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Which OpenAI chat model the agents use. Default is the cheap/fast mini model.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Temperature controls creativity: 0 = focused/repeatable, 1 = more varied.
# We keep it low-ish so itineraries stay sensible.
LLM_TEMPERATURE = 0.3

# Model used to transcribe microphone audio into text.
WHISPER_MODEL = "whisper-1"

# --- Agent / graph behaviour ----------------------------------------------
# If the plan goes over budget, how many times may the team re-plan (cheaper)
# before we give up and just present the closest option? Caps the loop so the
# graph can never run forever.
MAX_BUDGET_REVISIONS = 1

# Sensible fallbacks if the user never states them in their request.
DEFAULT_DAYS = 2
DEFAULT_BUDGET = 30000.0          # in local currency units (e.g. INR)
DEFAULT_CURRENCY = "INR"


def is_llm_configured() -> bool:
    """True only when an OpenAI key is present.

    The Gradio app uses this to show a friendly 'add your key' message instead
    of crashing when the .env is empty.
    """
    return bool(OPENAI_API_KEY)
