import operator
from typing import Annotated, List, Literal, TypedDict, Union
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# --- 1. Define Helper Types ---

class ItineraryItem(TypedDict):
    """Represents a single booked item in the trip."""
    name: str
    cost: float
    type: Literal["flight", "hotel", "activity", "transport"]
    status: Literal["confirmed", "pending"]

# --- 2. Define Reducer Functions ---

def reduce_itinerary(current: List[ItineraryItem] | None, new: List[ItineraryItem] | None) -> List[ItineraryItem]:
    """Appends new bookings to the itinerary list."""
    if current is None:
        current = []
    if new is None:
        new = []
    return current + new

# --- 3. Define the Core Agent State ---

class TravelState(TypedDict):
    """
    The Single Source of Truth for the Agent.
    """
    # Standard chat history (User: "Plan trip", AI: "Sure")
    messages: Annotated[List[BaseMessage], add_messages]
    
    # THE LEDGER: These are critical variables the LLM cannot 'hallucinate' changes to.
    # Only tools can update these via Command().
    total_budget: float      # The user's initial limit (e.g., 2000.0)
    remaining_budget: float  # The current balance (e.g., 1250.0)
    
    # The list of what we have actually booked
    itinerary: Annotated[List[ItineraryItem], reduce_itinerary]
    
    # Track the current location for finding nearby places
    current_location: str