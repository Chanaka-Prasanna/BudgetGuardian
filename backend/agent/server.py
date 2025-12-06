import json
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import AsyncGenerator

# Import the graph we built in Phase 1
# Ensure main.py has `app = create_react_agent(...)` exposed
from main import app as agent_graph

app = FastAPI(title="BudgetGuardian API")

# Allow Next.js (usually localhost:3000) to call us
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

async def event_generator(query: str, budget: float, location: str) -> AsyncGenerator[str, None]:
    """
    Streams LangGraph events to the client in SSE format.
    """
    # 1. Initialize the Agent's Memory
    initial_state = {
        "messages": [("user", query)],
        "total_budget": budget,
        "remaining_budget": budget,
        "itinerary": [],
        "current_location": location
    }

    # 2. Async Stream from LangGraph
    # stream_mode="values" gives us the full state after every node execution
    async for event in agent_graph.astream(initial_state, stream_mode="values"):
        
        payload = {}

        # --- Detect Message Updates (Thoughts/Tool Calls) ---
        if "messages" in event and event["messages"]:
            last_msg = event["messages"][-1]
            payload["type"] = "message"
            payload["data"] = {
                "role": last_msg.type, # 'ai', 'human', or 'tool'
                "content": str(last_msg.content)
            }
        
        # --- Detect Ledger Updates (The "CV Feature") ---
        # If the remaining budget changed or itinerary grew, send a special event
        if "remaining_budget" in event:
            payload["type"] = "ledger_update"
            payload["data"] = {
                "remaining": event["remaining_budget"],
                "total": event["total_budget"],
                "itinerary": event.get("itinerary", [])
            }

        # 3. Format as Server-Sent Event (data: json\n\n)
        if payload:
            json_data = json.dumps(payload)
            yield f"data: {json_data}\n\n"
            # Small yield context switch to ensure smooth streaming
            await asyncio.sleep(0.01)

    # 4. Signal End of Stream
    yield "data: [DONE]\n\n"

@app.post("/api/plan")
async def plan_trip(request: TripRequest):
    """
    Connects the frontend to the agent stream.
    """
    print(f"Received request: {request.query} with budget ${request.budget}")
    return StreamingResponse(
        event_generator(request.query, request.budget, request.location),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    # running on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)