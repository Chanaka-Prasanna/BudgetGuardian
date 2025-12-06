import uuid
from typing import Annotated, Literal

from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import InjectedState
from langchain_core.tools import InjectedToolCallId
from langgraph.types import Command

import os
import requests
import json

PRICE_MAP = {
    "PRICE_LEVEL_FREE": 0.0,
    "PRICE_LEVEL_INEXPENSIVE": 100.0,  # e.g., $100/night
    "PRICE_LEVEL_MODERATE": 200.0,
    "PRICE_LEVEL_EXPENSIVE": 450.0,
    "PRICE_LEVEL_VERY_EXPENSIVE": 800.0,
    "UNSPECIFIED": 150.0 # Fallback average
}

# Import the state definition we just made
# from state import TravelState, ItineraryItem 

@tool
def book_hotel(
    hotel_name: str, 
    nightly_rate: float, 
    nights: int,
    state: Annotated[dict, InjectedState], # <--- Magic: Access real ledger
    tool_call_id: Annotated[str, InjectedToolCallId] # <--- Get the actual tool call ID
) -> Command:
    """
    Book a hotel. verification of funds happens BEFORE booking.
    
    Args:
        hotel_name: Name of the hotel to book.
        nightly_rate: The cost per night (from search results).
        nights: Number of nights to stay.
    """
    
    # 1. Calculate Total Cost
    total_cost = nightly_rate * nights
    
    # 2. READ THE LEDGER (Critical Step)
    current_balance = state.get("remaining_budget", 0)
    
    # 3. ENFORCE CONSTRAINTS
    # If the agent tries to spend money it doesn't have, we reject the action.
    if total_cost > current_balance:
        return Command(
            update={
                # We do NOT update budget or itinerary here.
                # We only add a tool message telling the LLM it failed.
                "messages": [
                    ToolMessage(
                        content=f"Error: Transaction Declined. Cost ${total_cost} exceeds remaining budget of ${current_balance}. Please find a cheaper option.",
                        tool_call_id=tool_call_id # Use the actual tool call ID
                    )
                ]
            }
        )

    # 4. EXECUTE TRANSACTION (If funds exist)
    new_balance = current_balance - total_cost
    
    print(f"💰 BOOKING APPROVED: {hotel_name} for ${total_cost}. New Balance: ${new_balance}")

    # 5. COMMIT TO STATE
    return Command(
        update={
            # Update the numerical ledger
            "remaining_budget": new_balance,
            
            # Add to the structured itinerary list
            "itinerary": [{
                "name": hotel_name,
                "cost": total_cost,
                "type": "hotel",
                "status": "confirmed"
            }],
            
            # Tell the LLM what happened so it can reply to the user
            "messages": [
                ToolMessage(
                    content=f"Successfully booked {hotel_name} for {nights} nights. Total: ${total_cost}. Remaining Budget: ${new_balance}",
                    tool_call_id=tool_call_id # Use the actual tool call ID
                )
            ]
        }
    )


@tool
def search_hotels(location: str, budget_tier: str = "moderate") -> str:
    """
    Search for real hotels using Google Places API. 
    Returns a list of options with names and ESTIMATED nightly rates.
    
    Args:
        location: The city or area to search (e.g., "Shinjuku, Tokyo").
        budget_tier: Preference (cheap, moderate, luxury) to help filter.
    """
    
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY not found in environment variables."

    # 1. Prepare the Real API Request
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        # Field Masking is a pro move: reduce latency/cost by asking only for what we need
        "X-Goog-FieldMask": "places.displayName,places.priceLevel,places.formattedAddress"
    }
    
    payload = {
        "textQuery": f"hotels in {location}",
        "maxResultCount": 5
    }

    # 2. Call Google Cloud
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return f"API Error: Failed to fetch places. Details: {str(e)}"

    # 3. Parse & Normalize Data
    results = []
    if "places" not in data:
        return "No hotels found. Try a different location."

    for place in data["places"]:
        name = place.get("displayName", {}).get("text", "Unknown Hotel")
        price_level = place.get("priceLevel", "UNSPECIFIED")
        address = place.get("formattedAddress", "Address unknown")
        
        # Convert Enum to Float for our Ledger
        estimated_cost = PRICE_MAP.get(price_level, 150.0)
        
        results.append(
            f"- Name: {name}\n  Address: {address}\n  Est. Rate: ${estimated_cost} (Level: {price_level})"
        )

    # 4. Return formatted text for the LLM to read
    return "\n".join(results)