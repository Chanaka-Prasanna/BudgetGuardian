from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

from graph import app

# The 'app' is now imported from graph.py which contains the Multi-Agent Supervisor Graph

# --- HOW TO RUN IT ---
if __name__ == "__main__":
    # Initialize with a budget
    initial_state = {
        "messages": [("user", "Plan a trip to Tokyo from NYC. I need a flight and a hotel for 3 nights. Budget is $2500.")],
        "total_budget": 2500.0,
        "remaining_budget": 2500.0,
        "itinerary": [],
        "current_location": "NYC",
        "next": "Supervisor" # Start with Supervisor
    }

    print("🤖 Multi-Agent System Starting...")
    
    # Run the graph
    for chunk in app.stream(initial_state, stream_mode="values"):
        # Pretty print the last message
        if "messages" in chunk and chunk["messages"]:
            last_msg = chunk["messages"][-1]
            print(f"\n[{last_msg.type.upper()}]: {last_msg.content}")
            
        # Check if budget updated
        if "remaining_budget" in chunk:
             print(f"💰 Ledger Update: Remaining Funds = ${chunk['remaining_budget']}")
             
        # Show who is acting
        if "next" in chunk:
            print(f"👉 Next Agent: {chunk['next']}")