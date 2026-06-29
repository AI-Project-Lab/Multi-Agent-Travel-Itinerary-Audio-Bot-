"""build_graph.py — assemble the agents into a LangGraph StateGraph.

This is where multi-agent ORCHESTRATION actually happens. We declare the team
members (nodes) and how work flows between them (edges):

        START
          |
          v
      supervisor                 (parse request: destination, days, budget...)
       /  |  |  \\                 <-- FAN-OUT: 4 specialists run IN PARALLEL
   transport accommodation activities food
       \\  |  |  /
          v                      <-- FAN-IN: wait for all four, then check money
        budget
        /     \\                  <-- CONDITIONAL EDGE (the budget loop)
   replan      done
  (back to      |
  supervisor)   v
            compiler             (write the final day-by-day itinerary)
                |
                v
               END

Key LangGraph ideas shown here:
  * StateGraph        — a graph whose nodes share one state object (state.py)
  * add_edge          — an unconditional "go from A to B"
  * parallel fan-out  — several edges leaving the same node run together
  * fan-in            — a node with several incoming edges waits for all of them
  * conditional edge  — a function decides the next node (our budget loop)
  * checkpointer      — saves state so a run can be resumed / inspected (memory)
"""

from functools import lru_cache

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from genai_voice.agents.accommodation import accommodation_node
from genai_voice.agents.activities import activities_node
from genai_voice.agents.budget_agent import budget_node, budget_router
from genai_voice.agents.compiler import compiler_node
from genai_voice.agents.food import food_node
from genai_voice.agents.supervisor import supervisor_node
from genai_voice.agents.transport import transport_node
from genai_voice.state import ItineraryState

# The four specialists that run in parallel. Listing them once keeps the wiring
# below short and avoids typos.
SPECIALISTS = {
    "transport": transport_node,
    "accommodation": accommodation_node,
    "activities": activities_node,
    "food": food_node,
}


def _build() -> StateGraph:
    """Create and connect the graph (not yet compiled)."""
    builder = StateGraph(ItineraryState)

    # 1) Register every agent as a node.
    builder.add_node("supervisor", supervisor_node)
    for name, node_fn in SPECIALISTS.items():
        builder.add_node(name, node_fn)
    builder.add_node("budget", budget_node)
    builder.add_node("compiler", compiler_node)

    # 2) Entry point: start with the supervisor.
    builder.add_edge(START, "supervisor")

    # 3) FAN-OUT: supervisor -> each specialist. Because they all leave the same
    #    node, LangGraph runs the four specialists in parallel.
    for name in SPECIALISTS:
        builder.add_edge("supervisor", name)

    # 4) FAN-IN: each specialist -> budget. The budget node has four incoming
    #    edges, so LangGraph waits for ALL specialists to finish before running it.
    for name in SPECIALISTS:
        builder.add_edge(name, "budget")

    # 5) CONDITIONAL EDGE (the budget loop). budget_router returns "replan" or
    #    "done"; we map those strings to the next node.
    builder.add_conditional_edges(
        "budget",
        budget_router,
        {
            "replan": "supervisor",  # over budget -> try again, cheaper
            "done": "compiler",      # within budget -> write the itinerary
        },
    )

    # 6) Finish after the compiler writes the plan.
    builder.add_edge("compiler", END)

    return builder


@lru_cache(maxsize=1)
def get_graph():
    """Build & compile the graph once, then reuse it (it is stateless to reuse).

    We attach a MemorySaver checkpointer: it stores the state for each run under a
    `thread_id`, which is what makes resuming and step-by-step inspection possible.
    """
    return _build().compile(checkpointer=MemorySaver())
