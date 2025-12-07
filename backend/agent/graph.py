from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from state import TravelState
from agents import search_node, research_node, itinerary_node, supervisor_node

# 1. Initialize the Graph
workflow = StateGraph(TravelState)

# 2. Add Nodes for the new workflow:
# START -> Supervisor -> Search -> HITL (Select Places) -> Research -> HITL (Choose Locations) -> Itinerary -> END

workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Search_Agent", search_node)
workflow.add_node("Research_Agent", research_node)
workflow.add_node("Itinerary_Agent", itinerary_node)

# 3. Define Edges
workflow.add_edge(START, "Supervisor")
workflow.add_edge("Search_Agent", "Supervisor")
workflow.add_edge("Research_Agent", "Supervisor")
workflow.add_edge("Itinerary_Agent", "Supervisor")

# 4. Conditional Logic (Router)
def decide_next(state: TravelState) -> str:
    """
    Supervisor decides which agent to call next based on workflow_stage.
    """
    next_agent = state.get("next", "FINISH")
    print(f"🔄 Supervisor routing to: {next_agent}")
    return next_agent

workflow.add_conditional_edges(
    "Supervisor",
    decide_next,
    {
        "Search_Agent": "Search_Agent",
        "Research_Agent": "Research_Agent",
        "Itinerary_Agent": "Itinerary_Agent",
        "FINISH": END
    }
)

# 5. Compile with Interrupts for Human-in-the-Loop
# Interrupt AFTER Search (so user can select places)
# Interrupt AFTER Research (so user can choose which locations to include in itinerary)
checkpointer = MemorySaver()
app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_after=["Search_Agent", "Research_Agent"]  # Changed to interrupt_after
)
