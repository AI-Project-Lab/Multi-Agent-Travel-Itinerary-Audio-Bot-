"""llm.py — one tiny helper that hands every agent the same chat model.

Why a shared helper instead of creating ChatOpenAI in each agent file?
  * One place to change the model name / temperature.
  * One place to give a friendly error if the API key is missing.
  * Beginners only have to learn ONE way to get an LLM.

We use `ChatOpenAI` from the `langchain-openai` package. LangChain wraps the
OpenAI API in a uniform interface that LangGraph understands (messages in,
message out, with optional tool-calling and structured output).
"""

from functools import lru_cache

from langchain_openai import ChatOpenAI

from genai_voice.config import defaults


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    """Return a ready-to-use chat model, shared across all agents.

    `@lru_cache` means the ChatOpenAI object is created once and reused, instead
    of rebuilding it on every agent call (a small but nice efficiency win).
    """
    if not defaults.is_llm_configured():
        # Fail loudly but kindly — this is the #1 setup mistake in class.
        raise RuntimeError(
            "OPENAI_API_KEY is not set.\n"
            "Fix: copy .env_template to .env and paste your OpenAI key into it."
        )

    return ChatOpenAI(
        model=defaults.OPENAI_MODEL,
        temperature=defaults.LLM_TEMPERATURE,
        api_key=defaults.OPENAI_API_KEY,
    )
