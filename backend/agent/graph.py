from langgraph.graph import StateGraph, START, END
from state import TravelState
from agents import hotel_node, flight_node, supervisor_node

# 1. Initialize the Graph
workflow = StateGraph(TravelState)

# 2. Add Nodes
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Hotel_Scout", hotel_node)
workflow.add_node("Flight_Specialist", flight_node)

# 3. Define Edges
# Start at Supervisor
workflow.add_edge(START, "Supervisor")

# From Workers back to Supervisor
workflow.add_edge("Hotel_Scout", "Supervisor")
workflow.add_edge("Flight_Specialist", "Supervisor")

# 4. Conditional Logic (Router)
def decide_next(state: TravelState) -> str:
    return state["next"]

workflow.add_conditional_edges(
    "Supervisor",
    decide_next,
    {
        "Hotel_Scout": "Hotel_Scout",
        "Flight_Specialist": "Flight_Specialist",
        "FINISH": END
    }
)

# 5. Compile
app = workflow.compile()
