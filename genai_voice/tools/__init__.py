"""tools package — the concrete 'skills' the agents use to fetch real data.

Each specialist agent is paired with a tool here. Giving every agent a DISTINCT
tool is what makes this a real multi-agent system instead of one LLM pretending
to be several (we call that "orchestration theatre").

NOTE FOR LEARNERS: the tools below return realistic *sample* data so the project
runs in class with only an OpenAI key (no extra paid APIs, no flaky scraping).
Each function has a comment showing where you would plug in a real source —
e.g. Playwright web scraping (already a project dependency) or a weather API.
"""
