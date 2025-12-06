from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from state import TravelState
from tools import book_hotel, search_hotels

# 1. Setup the Brain (Gemini Flash is fast & cheap)
# Ensure GOOGLE_API_KEY is set in env for Gemini
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

# 2. Define the Toolkit
tools = [search_hotels, book_hotel]

# 3. Create the Graph
# We pass our custom TravelState schema here
app = create_react_agent(model, tools, state_schema=TravelState)

# --- HOW TO RUN IT ---
if __name__ == "__main__":
    # Initialize with a budget
    initial_state = {
        "messages": [("user", "Plan a 3-night stay in Tokyo. My total budget is $1000.")],
        "total_budget": 1000.0,
        "remaining_budget": 1000.0, # Sync initially
        "itinerary": [],
        "current_location": "Tokyo"
    }

    print("🤖 Agent Starting...")
    
    # Run the graph
    for chunk in app.stream(initial_state, stream_mode="values"):
        # Pretty print the last message
        if chunk["messages"]:
            last_msg = chunk["messages"][-1]
            print(f"\n[{last_msg.type.upper()}]: {last_msg.content}")
            
        # Check if budget updated
        if "remaining_budget" in chunk:
             print(f"💰 Ledger Update: Remaining Funds = ${chunk['remaining_budget']}")