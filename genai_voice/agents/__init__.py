"""agents package — one module per agent (the 'team members').

Each agent is just a plain Python function called a NODE. A node:
  1. receives the shared `state` (see genai_voice/state.py),
  2. does one focused job (often using a tool),
  3. returns a small dict of updates to merge back into the state.

The supervisor decides the plan; the four specialists each cover one area; the
budget agent checks the money; the compiler writes the final itinerary.
"""
