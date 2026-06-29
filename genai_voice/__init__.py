"""genai_voice — the core package for the Multi-Agent Travel Itinerary Audio Bot.

Big picture of how the pieces fit together:

    voice in  ->  processing/audio.py  (speech -> text using Whisper)
                       |
                       v
              graph/runner.py  ->  graph/build_graph.py  (the LangGraph "brain")
                       |                     |
                       |                     +-- agents/   (supervisor + specialists)
                       |                     +-- tools/    (web, weather, budget helpers)
                       |                     +-- state.py  (the shared memory of the graph)
                       v
              processing/audio.py  (text -> speech using gTTS)  ->  voice out

Read the modules in roughly that order if you are new to the project.
"""
