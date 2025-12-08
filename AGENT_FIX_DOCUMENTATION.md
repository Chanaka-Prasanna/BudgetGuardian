# Agent Research Flow Fix

## Problem
When users selected place numbers (e.g., 1, 2, 3) for research, the agent would receive the place IDs in the state but would keep asking "OK, please provide the place IDs of the locations you'd like me to research" instead of proceeding with the research.

## Root Cause
The Research Agent (created using `create_react_agent`) was receiving the `selected_places` in the state, but it wasn't explicitly informed about which places to research in its conversation context. The agent's system prompt mentioned that "the place IDs are in state['selected_places']" but the ReAct agent doesn't automatically inspect state fields - it needs explicit instructions in the message history.

## Solution

### Research Node Fix
Modified `research_node()` in `backend/agent/agents.py` to:
1. Extract `selected_places` from the state
2. Map place IDs to their names from `found_places`
3. Create an explicit HumanMessage with the list of place IDs to research
4. Pass this enriched state to the research agent

```python
research_instruction = (
    f"I have selected {len(selected_places)} places for you to research. "
    f"Here are the place IDs you need to research:\n"
    + "\n".join(place_details) +
    "\n\nPlease call the research_place tool for EACH of these place IDs and provide a comprehensive summary."
)
```

### Itinerary Node Fix
Applied the same pattern to `itinerary_node()` to ensure the agent knows exactly which location to plan for:
- Extracts the chosen location from `selected_places`
- Creates an explicit instruction message with the location name and budget
- Passes this to the itinerary agent

## Result
Now when users provide place numbers:
1. Frontend converts numbers → place IDs
2. Backend updates state with `selected_places`
3. Graph resumes and routes to Research_Agent
4. Research_Agent receives explicit instruction message with place IDs
5. Agent proceeds with research immediately instead of asking again

## Testing
Restart the backend server for changes to take effect:
```bash
cd backend/agent
python server.py
```

Then test the flow:
1. Start a new trip with location and budget
2. Wait for search results
3. Enter place numbers (e.g., "1, 3, 5")
4. Agent should now proceed directly with research instead of asking again

