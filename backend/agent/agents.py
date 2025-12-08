from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from tools import search_places, research_place
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
    [search_places],  # Only search for places, no flight searches needed
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
    system_prompt="""You are a Travel Research Agent. Conduct thorough research and provide COMPREHENSIVE, DETAILED information.

Task:
1. Call research_place for EACH place ID provided
2. For each location, present DETAILED information including:
   - Full description and overview
   - Historical background and significance
   - Weather conditions and best time to visit
   - Popular attractions and activities nearby
   - Cultural aspects and local customs
   - Transportation options
   - Estimated costs and budget considerations
   - Pros and cons
   - Traveler tips and recommendations
   - Any unique features or special notes

3. After researching ALL locations, provide a DETAILED comparison
4. Ask user to select ONE location for their itinerary

IMPORTANT: Provide COMPREHENSIVE details, not just brief summaries. Users want to see extensive research results to make informed decisions.
"""
)

def research_node(state: TravelState) -> dict:
    """Entry point for the Research Agent. Performs parallel research on selected places."""
    # Get selected place IDs from state
    selected_places = state.get("selected_places", [])
    found_places = state.get("found_places", [])
    
    # Build a mapping of IDs to names for better context
    place_details = []
    for place_id in selected_places:
        place = next((p for p in found_places if p.get("id") == place_id), None)
        if place:
            place_details.append(f"- {place_id}: {place.get('name', 'Unknown')}")
    
    # Create an explicit message with the place IDs to research
    research_instruction = (
        f"I have selected {len(selected_places)} places for you to research. "
        f"Here are the place IDs you need to research:\n"
        + "\n".join(place_details) +
        "\n\nPlease call the research_place tool for EACH of these place IDs and provide COMPREHENSIVE, DETAILED research results. "
        "I want to see extensive information about each location including history, weather, attractions, costs, pros/cons, and tips. "
        "Don't just give brief summaries - provide thorough details so I can make an informed decision."
    )
    
    # Add this as a human message to explicitly tell the agent what to do
    state_with_instruction = dict(state)
    state_with_instruction["messages"] = state["messages"] + [HumanMessage(content=research_instruction)]
    
    result = research_agent.invoke(state_with_instruction)
    # Update workflow stage to indicate we're waiting for user to choose locations
    result["workflow_stage"] = "choose_locations"
    return result


# --- Itinerary Agent (Planner) ---
itinerary_agent = create_agent(
    llm,
    [],  # No tools needed - just planning and recommendations
    system_prompt="""You are the Itinerary Planning Agent. Create detailed travel plans based on user preferences.

Your Tasks:
1. **Initial Itinerary**: Create a comprehensive day-by-day plan with accommodations, activities, dining, and costs
2. **Adjustments**: When user requests changes, MODIFY the previous itinerary based on their feedback
   - Read their adjustment request carefully
   - Make SPECIFIC changes they asked for
   - Keep parts they didn't mention changing
   - Explain what you changed

Important:
- When adjusting, DO NOT just repeat the same itinerary
- Actually implement the changes the user requested
- If they say "add more activities" - ADD MORE, don't keep the same
- If they say "change hotel to budget" - CHANGE IT to a budget option
- If they say "extend to 3 days" - ADD another day

Always include cost estimates and stay within budget.
"""
)

def itinerary_node(state: TravelState) -> dict:
    """Entry point for the Itinerary Agent."""
    # Check if this is an adjustment request by looking at the last message
    messages = state.get("messages", [])
    workflow_stage = state.get("workflow_stage", "")
    
    # If workflow_stage is already review_itinerary, this is an adjustment request
    is_adjustment = workflow_stage == "review_itinerary"
    
    if is_adjustment:
        # For adjustments, the user's message is already in the state
        # Just invoke the agent directly - it will see the conversation history
        result = itinerary_agent.invoke(state)
    else:
        # This is the initial itinerary creation
        selected_places = state.get("selected_places", [])
        researched_places = state.get("researched_places", [])
        remaining_budget = state.get("remaining_budget", 0)
        
        # Get details of the chosen location
        if selected_places and len(selected_places) > 0:
            chosen_place_id = selected_places[0]  # Should be only ONE location at this stage
            chosen_place = next((p for p in researched_places if p.get("id") == chosen_place_id), None)
            
            if chosen_place:
                itinerary_instruction = (
                    f"I have selected {chosen_place.get('name', 'this location')} for my trip. "
                    f"My budget is ${remaining_budget:.2f}. "
                    f"Please create a detailed day-by-day itinerary with recommendations for accommodation, "
                    f"activities, dining, and transportation. Include estimated costs for everything!"
                )
            else:
                itinerary_instruction = (
                    f"I have selected a location (ID: {chosen_place_id}) for my trip. "
                    f"My budget is ${remaining_budget:.2f}. "
                    f"Please create a detailed itinerary with cost estimates."
                )
        else:
            itinerary_instruction = (
                f"Please create a detailed itinerary for the selected location. "
                f"My budget is ${remaining_budget:.2f}."
            )
        
        # Add explicit instruction as a human message
        state_with_instruction = dict(state)
        state_with_instruction["messages"] = state["messages"] + [HumanMessage(content=itinerary_instruction)]
        
        result = itinerary_agent.invoke(state_with_instruction)
    
    # Mark workflow stage as review_itinerary so user can provide feedback
    result["workflow_stage"] = "review_itinerary"
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
    "\n\n5. INITIAL ITINERARY: Create initial travel plan for ONE location"
    "   → Route to Itinerary_Agent to build detailed itinerary around the chosen location"
    "\n\n6. REVIEW: Initial itinerary created, waiting for user feedback"
    "   → Check workflow_stage='review_itinerary'"
    "   → If user provided adjustment requests, route to Itinerary_Agent to refine"
    "   → If user confirmed (no changes needed), respond with FINISH"
    "\n\n7. COMPLETE: Final itinerary approved"
    "   → Check workflow_stage='complete'"
    "   → Respond with FINISH"
    "\n\n"
    "DECISION RULES:"
    "\n- If workflow_stage is empty or 'init' or 'search' → Search_Agent" 
    "\n- If workflow_stage='select_locations' AND selected_places exist → Research_Agent"
    "\n- If workflow_stage='choose_locations' AND selected_places has ONE item → Itinerary_Agent"
    "\n- If workflow_stage='review_itinerary' AND user provided feedback → Itinerary_Agent"
    "\n- If workflow_stage='review_itinerary' AND user confirmed → FINISH"
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
