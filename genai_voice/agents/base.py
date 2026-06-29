"""base.py — small shared helpers used by every agent.

Putting the repeated bits here (calling the LLM, writing a scratchpad note) keeps
each agent file short and avoids copy-paste mistakes. This is the DRY principle:
"Don't Repeat Yourself".
"""

from langchain_core.messages import HumanMessage, SystemMessage

from genai_voice.models.llm import get_llm


def ask_llm(system_prompt: str, user_content: str) -> str:
    """Send a system prompt + the user content to the model and return its text.

    This is the one and only place we actually call the LLM, so every agent talks
    to the model the same way.
    """
    llm = get_llm()
    response = llm.invoke(
        [
            SystemMessage(content=system_prompt),   # the agent's role
            HumanMessage(content=user_content),      # the data to reason over
        ]
    )
    return response.content.strip()


def note(agent_name: str, text: str) -> list:
    """Create a one-line scratchpad note.

    We return a LIST with a single string because state['messages'] uses the
    `add` reducer (see state.py) — returning a list lets LangGraph merge notes
    from agents that run at the same time without clobbering each other.
    """
    return [f"[{agent_name}] {text}"]
