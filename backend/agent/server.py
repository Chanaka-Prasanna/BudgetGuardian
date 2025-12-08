import json
import asyncio
import uuid
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import AsyncGenerator, List, Optional
from langchain_core.messages import HumanMessage

# Import the agent - using Supervisor graph
from graph import app as agent_graph

app = FastAPI(title="BudgetGuardian API")

# Allow Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TripRequest(BaseModel):
    query: str
    budget: float
    location: str
    description: str = ""  # User's description of what they're looking for

class ResumeRequest(BaseModel):
    thread_id: str
    selected_places: Optional[List[str]] = None
    message: str = ""
    action: str = "research"  # "research" or "plan_itinerary"

async def event_generator(input_data: dict | None, thread_id: str) -> AsyncGenerator[str, None]:
    """
    Streams LangGraph events to the client in SSE format.
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    # Track seen messages to avoid duplicates
    seen_message_count = 0
    
    try:
        # Send thread_id first so frontend can save it
        yield f"data: {json.dumps({'type': 'meta', 'thread_id': thread_id})}\n\n"

        # Async Stream from LangGraph
        async for event in agent_graph.astream(input_data, config, stream_mode="values"):
            
            payload = {}

            # 1. Message Updates - Only send NEW messages
            if "messages" in event and event["messages"]:
                current_message_count = len(event["messages"])
                
                # Send only messages we haven't seen yet
                if current_message_count > seen_message_count:
                    for i in range(seen_message_count, current_message_count):
                        msg = event["messages"][i]
                        
                        # Filter messages: only show human and AI messages, skip tool calls and tool responses
                        if msg.type in ["human", "ai"]:
                            # Skip AI messages that are tool calls (have tool_calls attribute and it's not empty)
                            if msg.type == "ai" and hasattr(msg, 'tool_calls') and msg.tool_calls:
                                continue
                            
                            # Skip empty or very short AI messages that are just intermediate reasoning
                            if msg.type == "ai" and (not msg.content or len(str(msg.content).strip()) < 10):
                                continue
                                
                            payload = {
                                "type": "message",
                                "data": {
                                    "role": msg.type,
                                    "content": str(msg.content)
                                }
                            }
                            yield f"data: {json.dumps(payload)}\n\n"
                            await asyncio.sleep(0.01)
                    
                    seen_message_count = current_message_count
            
            # 2. Ledger Updates
            if "remaining_budget" in event:
                payload = {
                    "type": "ledger_update",
                    "data": {
                        "remaining": event["remaining_budget"],
                        "total": event["total_budget"],
                        "itinerary": event.get("itinerary", [])
                    }
                }
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.01)

            # 3. Map Updates (Found Places)
            if "found_places" in event and event["found_places"]:
                payload = {
                    "type": "map_update",
                    "data": event["found_places"]
                }
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.01)
            
            # 4. Research Updates
            if "researched_places" in event and event["researched_places"]:
                payload = {
                    "type": "research_update",
                    "data": event["researched_places"]
                }
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.01)
            
            # 5. Workflow Stage Updates
            if "workflow_stage" in event:
                payload = {
                    "type": "workflow_stage",
                    "data": event["workflow_stage"]
                }
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.01)

        # Check if paused or done
        state_snapshot = agent_graph.get_state(config)
        current_stage = state_snapshot.values.get("workflow_stage", "")
        
        # If workflow_stage is select_locations or choose_locations, we're paused
        if current_stage in ["select_locations", "choose_locations"]:
            yield f"data: {json.dumps({'type': 'status', 'data': 'paused', 'stage': current_stage})}\n\n"
        elif state_snapshot.next:
            # Graph is interrupted for some other reason
            yield f"data: {json.dumps({'type': 'status', 'data': 'paused', 'next': state_snapshot.next})}\n\n"
        else:
            yield "data: [DONE]\n\n"
    
    except Exception as e:
        print(f"Error in event generator: {e}")
        import traceback
        traceback.print_exc()
        yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

@app.post("/api/plan")
async def plan_trip(request: TripRequest):
    """
    Starts a new trip planning session.
    """
    print(f"Starting new trip: {request.query} in {request.location}")
    thread_id = f"trip_{uuid.uuid4()}"
    
    # Build the initial message including all user inputs
    # Only add description if it's different from the query to avoid duplication
    if request.description and request.description.strip() and request.description.strip() != request.query.strip():
        full_query = f"{request.query}. Location: {request.location}. Budget: ${request.budget}. Looking for: {request.description}"
    else:
        full_query = f"{request.query}. Location: {request.location}. Budget: ${request.budget}."
    
    initial_state = {
        "messages": [HumanMessage(content=full_query)],
        "total_budget": request.budget,
        "remaining_budget": request.budget,
        "itinerary": [],
        "current_location": request.location,
        "found_places": [],
        "selected_places": [],
        "research_notes": [],
        "researched_places": [],
        "user_description": request.description or request.query,
        "workflow_stage": "search",
        "next": "Supervisor",
        "remaining_steps": 25  # Default from create_react_agent
    }
    
    return StreamingResponse(
        event_generator(initial_state, thread_id),
        media_type="text/event-stream"
    )

@app.post("/api/resume")
async def resume_trip(request: ResumeRequest):
    """
    Resumes a paused session with user input (selected places or confirmation to plan).
    """
    print(f"Resuming trip {request.thread_id} - Action: {request.action}")
    
    config = {"configurable": {"thread_id": request.thread_id}}
    
    updates = {}
    
    # Handle different actions
    if request.action == "research" and request.selected_places:
        # User selected places, proceed to research
        print(f"📍 Selected places for research: {request.selected_places}")
        
        # Get current state to verify place IDs exist
        current_state = agent_graph.get_state(config)
        found_places = current_state.values.get("found_places", [])
        available_ids = [p.get("id") for p in found_places if "id" in p]
        
        print(f"📋 Available place IDs in state: {available_ids}")
        
        # Validate that selected places exist in found_places
        missing_places = [pid for pid in request.selected_places if pid not in available_ids]
        if missing_places:
            print(f"⚠️ WARNING: Some selected place IDs not found: {missing_places}")
        
        updates["selected_places"] = request.selected_places
        
        # Keep message simple - agent should use state, not parse message
        message = f"Please research the selected places. I have selected {len(request.selected_places)} location(s) to learn more about."
        
    elif request.action == "plan_itinerary" and request.selected_places:
        # User confirmed locations, proceed to itinerary
        print(f"🗺️ Creating itinerary for: {request.selected_places}")

        updates["selected_places"] = request.selected_places
        
        message = f"Great! Please create a detailed itinerary for my selected location. Remember to stay within my budget."
        
    else:
        # Generic resume
        message = request.message or "Please continue."
    
    # 1. Update state with any changes
    if updates:
        agent_graph.update_state(config, updates)
    
    # 2. Add user message to trigger next step  
    agent_graph.update_state(config, {"messages": [HumanMessage(content=message)]})
    
    # 3. Resume stream from current position
    return StreamingResponse(
        event_generator(None, request.thread_id),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)