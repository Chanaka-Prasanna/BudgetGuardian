from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from tools import search_places, book_hotel, search_flights, book_flight, research_place
from state import TravelState

# 1. Setup LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

# 2. Define Helper to Create Agents
def create_agent(llm, tools, system_prompt: str):
    """Creates a standard ReAct agent.
    
    Note: System prompts are kept concise to avoid exposing internal details to users.
    All agent instructions focus on user-facing behavior rather than implementation details.
    """
    # We must pass the state_schema so the agent knows about our custom fields (budget, places, etc.)
    return create_react_agent(llm, tools, prompt=system_prompt, state_schema=TravelState)

# 3. Define the Specialized Agents (Workers)

# --- Search Agent ---
search_agent = create_agent(
    llm, 
    [search_places, search_flights], 
    system_prompt="""You are a Travel Discovery Agent specializing in finding diverse locations.

Your job is to discover ALL types of relevant places based on the user's destination and preferences.

Search Strategy:
1. Review the user's destination and what they're looking for
2. Use 'search_places' tool MULTIPLE times with different place_types to build a comprehensive list:
   - "tourist_attraction" - landmarks, monuments, historical sites, heritage locations
   - "lodging" - hotels, hostels, accommodations  
   - "restaurant" - dining options
   - "museum" - museums and cultural centers
   - "park" - parks and natural attractions
   - "place_of_worship" - temples, churches, mosques
   
3. If the user mentions a specific place name, use the user_query parameter
4. Call search_places 2-3 times with different types to get variety
5. After searching, tell the user:
   - How many places you found
   - The variety (hotels, attractions, cities, etc.)
   - That they should review and select which ones to research further

Example: User wants "Paris, interested in history and food"
→ Search for tourist attractions in Paris
→ Search for museums in Paris  
→ Search for restaurants in Paris
→ Present the results and ask which to research

Remember: Give users many options to choose from!
"""
)

def search_node(state: TravelState) -> dict:
    """Entry point for the Search Agent."""
    result = search_agent.invoke(state)
    # Update workflow stage to indicate we're waiting for user selection
    result["workflow_stage"] = "select_locations"
    return result


# --- Research Agent ---
research_agent = create_agent(
    llm,
    [research_place],
    system_prompt="""You are a Travel Research Agent conducting in-depth analysis of locations.

Your task:
1. The user has selected places to research - the place IDs are in state['selected_places']
2. For each place ID, call research_place(place_id="<the_exact_id>") 
3. Use the exact IDs from the list without modification

After researching all locations:
- Provide a comprehensive summary with key highlights, weather, costs, and pros/cons
- Ask the user which ONE location they'd like to build their itinerary around
- The user will select their primary destination for the trip

Keep your communication friendly and helpful. Focus on presenting the research findings clearly.
"""
)

def research_node(state: TravelState) -> dict:
    """Entry point for the Research Agent. Performs parallel research on selected places."""
    result = research_agent.invoke(state)
    # Update workflow stage to indicate we're waiting for user to choose locations
    result["workflow_stage"] = "choose_locations"
    return result


# --- Itinerary Agent (Planner) ---
itinerary_agent = create_agent(
    llm,
    [book_hotel, book_flight],
    system_prompt="""You are the Itinerary Planning Agent creating detailed travel plans.

Your job is to create a complete day-by-day itinerary for the user's chosen location.

Planning Process:
1. The user has selected ONE location - review the research data for that place
2. Check the budget - you must stay within the remaining funds
3. Create a detailed itinerary including:
   - Day-by-day schedule
   - Accommodation bookings (use book_hotel)
   - Transportation (use book_flight if needed)
   - Best times to visit
   - Duration recommendations
   - Nearby activities
   - Meal suggestions
   - Total cost breakdown

Budget Management:
- Check remaining budget before each booking
- If budget is tight, suggest budget-friendly options
- Keep a 10% buffer for unexpected costs

Final Summary:
- Complete itinerary for the chosen location
- All confirmed bookings
- Itemized costs
- Remaining budget
- Travel tips for the location

Focus on building the entire trip around the user's chosen destination!
"""
)

def itinerary_node(state: TravelState) -> dict:
    """Entry point for the Itinerary Agent."""
    result = itinerary_agent.invoke(state)
    
    # Recalculate remaining budget to avoid concurrency issues in tools
    # We use the itinerary from the result (which includes new bookings)
    itinerary = result.get("itinerary", [])
    total_budget = state.get("total_budget", 0)
    
    start_budget = float(total_budget)
    used_budget = sum(float(item.get("cost", 0)) for item in itinerary)
    remaining = start_budget - used_budget
    
    # Update explicitly
    result["remaining_budget"] = remaining
    result["workflow_stage"] = "complete"
    return result


# 4. Define the Supervisor (Manager)

members = ["Search_Agent", "Research_Agent", "Itinerary_Agent"]
system_prompt = (
    "You are a supervisor managing a travel planning workflow with these agents: {members}."
    "\n\n"
    "WORKFLOW STAGES (in order):"
    "\n1. SEARCH: User provides destination and preferences"
    "   → Route to Search_Agent to find diverse places (hotels, attractions, cities, heritage sites)"
    "\n\n2. SELECT: Search completed, waiting for user to select places"
    "   → Check workflow_stage='select_locations'"
    "   → If user has provided selected_places, route to Research_Agent"
    "   → If no selection yet, tell user to select from found_places"
    "\n\n3. RESEARCH: User selected places, need detailed research"
    "   → Route to Research_Agent for Wikipedia, weather, and detailed info"
    "\n\n4. CHOOSE: Research completed, waiting for user to select ONE location"
    "   → Check workflow_stage='choose_locations'"
    "   → User must select EXACTLY ONE location for the itinerary"
    "   → If user confirmed ONE location, route to Itinerary_Agent"
    "   → If no selection yet, tell user to review research and select ONE location"
    "\n\n5. ITINERARY: Create final travel plan for ONE location"
    "   → Route to Itinerary_Agent to build detailed itinerary around the chosen location"
    "\n\n6. COMPLETE: Itinerary created"
    "   → Respond with FINISH"
    "\n\n"
    "DECISION RULES:"
    "\n- If workflow_stage is empty or 'init' or 'search' → Search_Agent" 
    "\n- If workflow_stage='select_locations' AND selected_places exist → Research_Agent"
    "\n- If workflow_stage='choose_locations' AND selected_places has ONE item → Itinerary_Agent"
    "\n- If workflow_stage='complete' → FINISH"
    "\n- If user asks to start over → Search_Agent"
)

options = ["FINISH"] + members

class RouteResponse(dict):
    next: str

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            "Given the conversation above, who should act next?"
            " Or should we FINISH? Select one of: {options}",
        ),
    ]
).partial(options=str(options), members=", ".join(members))

def supervisor_node(state: TravelState) -> dict:
    """
    The Supervisor decides which agent goes next.
    """
    supervisor_chain = prompt | llm.with_structured_output(
        {
            "name": "route",
            "description": "Select the next role.",
            "parameters": {
                "type": "object",
                "properties": {
                    "next": {
                        "type": "string",
                        "enum": options,
                    }
                },
                "required": ["next"],
            },
        }
    )
    
    result = supervisor_chain.invoke(state)
    return {"next": result["next"]}
