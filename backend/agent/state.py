from typing import Annotated, List, Literal, TypedDict
import operator
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# --- 1. Define Helper Types ---

class ItineraryItem(TypedDict):
    """Represents a single booked item in the trip."""
    name: str
    cost: float
    type: Literal["flight", "hotel", "activity", "transport", "visit"]
    status: Literal["confirmed", "pending"]

# --- 2. Define Reducer Functions ---

def reduce_itinerary(current: List[ItineraryItem] | None, new: List[ItineraryItem] | None) -> List[ItineraryItem]:
    """Appends new bookings to the itinerary list."""
    if current is None:
        current = []
    if new is None:
        new = []
    return current + new

def reduce_places(current: List[dict] | None, new: List[dict] | None) -> List[dict]:
    """
    Merges new places into the current list, deduplicating by 'id'.
    If a place with the same ID exists, the new one overwrites it.
    """
    if current is None:
        current = []
    if new is None:
        new = []
    
    # Create a dict for easy lookup/update
    places_map = {p["id"]: p for p in current}
    
    # Update with new places
    for p in new:
        places_map[p["id"]] = p
        
    # Return as list
    return list(places_map.values())

# --- 3. Define the Core Agent State ---

class TravelState(TypedDict):
    """
    The Single Source of Truth for the Agent.
    Tracks the entire travel planning workflow from search to itinerary.
    """
    # Standard chat history (User: "Plan trip", AI: "Sure")
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Budget tracking
    total_budget: float      # The user's initial limit (e.g., 5000.0)
    remaining_budget: float  # The current balance (e.g., 3500.0)
    
    # Itinerary - what we have actually planned/booked
    itinerary: Annotated[List[ItineraryItem], reduce_itinerary]
    
    # User inputs
    current_location: str     # Destination location (e.g., "Paris, France")
    user_description: str     # User's description of what they're looking for
    
    # Search results - places found by Google Maps API
    found_places: Annotated[List[dict], reduce_places]  # [{id, name, lat, lng, rating, price_level, type, address, types}]
    
    # HITL - Human in the Loop selections
    selected_places: List[str]    # [place_id_1, place_id_2] - IDs selected by user for research
    
    # Research results - detailed information about places
    researched_places: Annotated[List[dict], reduce_places]  # Detailed research results for selected places
    researched_places: Annotated[List[dict], reduce_places]  # Detailed research results for selected places
    research_notes: Annotated[List[str], operator.add]           # Summary of research findings
    
    # Workflow management
    workflow_stage: str           # Current stage: "search", "select_locations", "research", "choose_locations", "itinerary"
    next: str                     # Supervisor routing decision
    
    # Required by create_react_agent
    remaining_steps: int
