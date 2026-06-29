# 🧭 Multi-Agent Travel Itinerary Audio Bot

A **live guided project** that turns a single-LLM voice chatbot into a **team of AI
agents** using **LangGraph**. You *speak* a travel request — "Plan a 2-day trip to Goa
with beach activities" — and a coordinated team of agents researches transport, stay,
activities, food, and budget, then writes a day-by-day itinerary and **reads it back to you**.

> 📚 New here? Read [`MULTI_AGENT_GUIDED_PROJECT_PLAN.md`](MULTI_AGENT_GUIDED_PROJECT_PLAN.md)
> first — it is the session-by-session teaching plan this code follows.

---

## What you'll learn (multi-agent concepts)

| Concept | Where it lives in the code |
|---|---|
| **Shared state** that flows between agents | [`genai_voice/state.py`](genai_voice/state.py) |
| **Supervisor / router** (parses request, coordinates) | [`genai_voice/agents/supervisor.py`](genai_voice/agents/supervisor.py) |
| **Tool-using specialist agents** | [`genai_voice/agents/`](genai_voice/agents/) + [`genai_voice/tools/`](genai_voice/tools/) |
| **Parallel fan-out / fan-in** | [`genai_voice/graph/build_graph.py`](genai_voice/graph/build_graph.py) |
| **Conditional loop** (re-plan if over budget) | [`genai_voice/agents/budget_agent.py`](genai_voice/agents/budget_agent.py) |
| **Synthesis agent** (final writer) | [`genai_voice/agents/compiler.py`](genai_voice/agents/compiler.py) |
| **Memory / checkpointer** | [`genai_voice/graph/build_graph.py`](genai_voice/graph/build_graph.py) |
| **Voice in/out** (Whisper + gTTS) | [`genai_voice/processing/audio.py`](genai_voice/processing/audio.py) |

---

## How the agent team works

```
        🎤 voice → Whisper → text
                    │
                    ▼
                supervisor          parse: destination, days, budget, preferences
              /   |    |    \        ── FAN-OUT: 4 specialists run in PARALLEL ──
       transport stay activities food   (each uses its own tool)
              \   |    |    /
                    ▼               ── FAN-IN: wait for all four ──
                 budget             add up costs; within budget?
                /      \            ── CONDITIONAL LOOP ──
           replan       done
         (cheaper)        │
                          ▼
                       compiler      writes the friendly day-by-day plan
                          │
                          ▼
                 text → gTTS → 🔊 voice
```

Every agent is just a small, well-commented Python function. Start reading at
`state.py`, then `agents/supervisor.py`, then `graph/build_graph.py`.

---

## Project structure

```
genai_voice/
├── config/defaults.py     # all settings in one place (model, budget, paths)
├── state.py               # the shared "travel notebook" passed between agents
├── models/llm.py          # one helper that gives every agent the chat model
├── tools/                 # the agents' skills (web lookups, weather, budget math)
├── agents/                # one file per agent (supervisor + 4 specialists + budget + compiler)
├── graph/                 # wires the agents into a LangGraph and runs it
└── processing/audio.py    # speech-to-text (Whisper) and text-to-speech (gTTS)
app/
└── chatbot_gradio_runner.py   # the Gradio web app (the "front door")
data/
└── travel_bot_context.txt     # brand voice/tone the writer agent follows
```

---

## Setup

> Tested with Python **3.10–3.12**. Uses **Poetry** for dependencies and **ffmpeg** for audio.

1. **Install** [Python](https://www.python.org/downloads/),
   [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer), and
   [ffmpeg](https://www.ffmpeg.org/download.html).
   - Windows: `ffmpeg.exe`/`ffprobe.exe` can be placed on your PATH.
   - Mac: `brew install ffmpeg`  ·  Linux: `apt install ffmpeg portaudio19-dev`

2. **Create a virtual environment** and install the project:
   ```bash
   python -m venv .venv
   # Windows:  .venv/Scripts/activate     Mac/Linux:  source .venv/bin/activate
   poetry lock
   poetry install
   ```

3. **Add your OpenAI key.** Copy the template and paste your key:
   ```bash
   cp .env_template .env        # then edit .env and set OPENAI_API_KEY=...
   ```
   Get a key at https://platform.openai.com/api-keys. Your `.env` is git-ignored.

---

## Run it

**Quick test (no microphone needed)** — run the agent team from the terminal:
```bash
poetry run RunItineraryGraph "Plan a 3-day budget trip to Jaipur, vegetarian food"
```
You'll see each agent's notes and the final itinerary printed out.

**Full voice web app:**
```bash
poetry run RunChatBotScript
```
Then open the local URL Gradio prints, record your request, edit the transcript,
and click **Plan my trip**.

---

## Notes for learners

- The lookup tools in `genai_voice/tools/web_search.py` return realistic **sample
  data** so the project runs in class with only an OpenAI key. Each function shows
  where you'd plug in a **real** source (Playwright scraping is already a dependency,
  or a flights/hotels/weather API).
- The "human-in-the-loop" step is the **editable transcript** before planning — you
  approve/fix what the team acts on.
- Want a challenge? See the **Stretch goals** in the project plan (weather-aware
  re-planning, a critic agent, peer-to-peer agent handoff).

---

## Troubleshooting

1. **"OPENAI_API_KEY is not set"** → copy `.env_template` to `.env` and add your key.
2. Microphone issues → use a headset, record in a quiet room, grant mic permission.
3. Audio errors → make sure `ffmpeg` is installed and on your PATH.
