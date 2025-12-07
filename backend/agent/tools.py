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

@tool
def book_hotel(
    hotel_name: str, 
    nightly_rate: float, 
    nights: int,
    state: Annotated[dict, InjectedState], 
    tool_call_id: Annotated[str, InjectedToolCallId] 
) -> Command:
    """
    Book a hotel. verification of funds happens BEFORE booking.
    """
    total_cost = nightly_rate * nights
    current_balance = state.get("remaining_budget", 0)
    
    if total_cost > current_balance:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error: Transaction Declined. Cost ${total_cost} exceeds remaining budget of ${current_balance}. Please find a cheaper option.",
                        tool_call_id=tool_call_id 
                    )
                ]
            }
        )

    new_balance = current_balance - total_cost
    print(f"💰 BOOKING APPROVED: {hotel_name} for ${total_cost}. New Balance: ${new_balance}")

    return Command(
        update={
            "itinerary": [{
                "name": hotel_name,
                "cost": total_cost,
                "type": "hotel",
                "status": "confirmed"
            }],
            "messages": [
                ToolMessage(
                    content=f"Successfully booked {hotel_name} for {nights} nights. Total: ${total_cost}. Remaining Budget: ${new_balance}",
                    tool_call_id=tool_call_id 
                )
            ]
        }
    )


@tool
def search_places(
    location: str, 
    place_type: str = "tourist_attraction",
    user_query: str = "",
    state: Annotated[dict, InjectedState] = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None
) -> Command:
    """
    Search for places using Google Places API based on user description.
    Supports ALL types of places:
    - tourist_attraction: Heritage sites, monuments, landmarks, historical places
    - lodging: Hotels, hostels, guesthouses
    - city_hall or locality: Cities and towns
    - restaurant: Dining options
    - museum: Museums and cultural centers
    - park: Parks and natural attractions
    - church/temple/mosque: Religious sites
    - And any other place type
    
    If user_query is specific (e.g., "Eiffel Tower"), searches for that exact place.
    Otherwise searches for place_type category in the location.
    Returns structured data for the map and text for the LLM.
    """
    
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    # Note: We continue even if no key, to trigger fallback
    
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key if api_key else "",
        "X-Goog-FieldMask": "places.displayName,places.priceLevel,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.types"
    }
    
    # Build search query based on user input
    if user_query and user_query.strip():
        # User specified exact place/query
        search_query = f"{user_query} in {location}"
    else:
        # Search by category
        search_query = f"{place_type} in {location}"
    
    payload = {
        "textQuery": search_query,
        "maxResultCount": 15  # Increased to get more diverse results
    }

    data = {}
    try:
        if api_key:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        print(f"API Error: {str(e)}")
        
    results = []
    found_places = []
    
    # FALLBACK MOCK DATA
    if "places" not in data or not data["places"]:
        print("⚠️ API returned no places. Using MOCK data.")
        data = {
            "places": [
                {
                    "displayName": {"text": f"Mock {place_type.capitalize()} 1"},
                    "formattedAddress": f"123 Mock St, {location}",
                    "rating": 4.5,
                    "location": {"latitude": 35.6895, "longitude": 139.6917},
                    "priceLevel": "PRICE_LEVEL_MODERATE"
                },
                {
                    "displayName": {"text": f"Mock {place_type.capitalize()} 2"},
                    "formattedAddress": f"456 Test Ave, {location}",
                    "rating": 4.2,
                    "location": {"latitude": 35.6890, "longitude": 139.7000},
                    "priceLevel": "PRICE_LEVEL_EXPENSIVE"
                }
            ]
        }

    for i, place in enumerate(data["places"]):
        name = place.get("displayName", {}).get("text", "Unknown")
        address = place.get("formattedAddress", "Address unknown")
        rating = place.get("rating", 0.0)
        price_level = place.get("priceLevel", "UNSPECIFIED")
        types = place.get("types", [])
        
        loc = place.get("location", {})
        lat = loc.get("latitude", 0.0)
        lng = loc.get("longitude", 0.0)
        
        # Generate unique ID
        place_id = f"place_{i}_{name.replace(' ', '_').lower()}"
        
        # Determine place category from types - more comprehensive categorization
        place_category = "place"  # default
        
        # Check types in order of priority for better categorization
        if "lodging" in types or "hotel" in types or "motel" in types:
            place_category = "hotel"
        elif "restaurant" in types or "cafe" in types or "food" in types or "bar" in types:
            place_category = "restaurant"
        elif "museum" in types:
            place_category = "museum"
        elif "park" in types or "natural_feature" in types or "campground" in types:
            place_category = "park"
        elif "hindu_temple" in types or "church" in types or "mosque" in types or "place_of_worship" in types or "synagogue" in types:
            place_category = "heritage"
        elif "locality" in types or "city_hall" in types or "administrative_area_level_1" in types or "political" in types:
            place_category = "city"
        elif "landmark" in types:
            place_category = "landmark"
        elif "tourist_attraction" in types or "point_of_interest" in types:
            place_category = "attraction"
        elif "establishment" in types:
            # Establishment is too generic, try to find more specific type
            for t in types:
                if t not in ["establishment", "point_of_interest"]:
                    place_category = t.replace("_", " ").title()
                    break
        
        # If still generic, use the first meaningful type from the list
        if place_category == "place" and types:
            # Skip generic types
            for t in types:
                if t not in ["establishment", "point_of_interest", "geocode"]:
                    place_category = t.replace("_", " ").title()
                    break
        
        found_places.append({
            "id": place_id,
            "name": name,
            "address": address,
            "lat": lat,
            "lng": lng,
            "rating": rating,
            "type": place_category,
            "price_level": price_level,
            "types": types
        })
        
        results.append(f"- {name} ({rating}★, {place_category}): {address}")

    return Command(
        update={
            "found_places": found_places,
            "messages": [
                ToolMessage(
                    content=f"Found {len(found_places)} {place_type}s in {location}. See map for details.",
                    tool_call_id=tool_call_id
                )
            ]
        }
    )

@tool
def get_wikipedia_info(place_name: str) -> str:
    """
    Fetch Wikipedia information about a place including historical significance,
    culture, attractions, and general information.
    """
    try:
        import wikipedia
        # Search for the place
        search_results = wikipedia.search(place_name, results=1)
        if not search_results:
            return f"No Wikipedia information found for {place_name}"
        
        # Get the page summary
        page = wikipedia.page(search_results[0], auto_suggest=False)
        summary = wikipedia.summary(search_results[0], sentences=5, auto_suggest=False)
        
        return f"""
**Wikipedia Information for {place_name}:**

{summary}

**Full Article**: {page.url}
"""
    except Exception as e:
        # Fallback for when Wikipedia API is not available or errors
        return f"""
**Wikipedia Information for {place_name}:**

{place_name} is a notable location with rich history and cultural significance.
Known for its unique attractions and local heritage, it draws visitors from around the world.

Note: For detailed information, visit Wikipedia directly.
"""

@tool
def get_weather_info(location: str) -> str:
    """
    Get current weather information for a location.
    Uses wttr.in free weather API.
    """
    try:
        import requests
        # Use wttr.in which doesn't require an API key
        url = f"https://wttr.in/{location}?format=j1"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            
            return f"""
**Weather in {location}:**
- Temperature: {current['temp_C']}°C ({current['temp_F']}°F)
- Condition: {current['weatherDesc'][0]['value']}
- Humidity: {current['humidity']}%
- Wind: {current['windspeedKmph']} km/h
- Feels Like: {current['FeelsLikeC']}°C
"""
        else:
            raise Exception("API request failed")
    except Exception as e:
        # Fallback weather info
        return f"""
**Weather in {location}:**
- Conditions vary by season
- Recommend checking local weather forecast before travel
- Pack for typical regional climate
"""

@tool
def research_place(
    place_id: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId] = None
) -> Command:
    """
    Research a specific place to get detailed info including:
    - Wikipedia information (history, culture)
    - Weather conditions
    - Ratings and reviews
    - Estimated costs
    - Travel tips
    
    Looks up the place from found_places using the place_id.
    """
    found_places = state.get("found_places", [])
    
    # Debug logging
    print(f"🔍 Research requested for place_id: {place_id}")
    print(f"📋 Found {len(found_places)} places in state")
    if found_places:
        print(f"📋 Available place IDs: {[p.get('id', 'NO_ID') for p in found_places]}")
    
    place = next((p for p in found_places if p.get("id") == place_id), None)
    
    if not place:
        # User-friendly error message without exposing system details
        if not found_places:
            error_msg = "I don't have any places to research. Let me search for places first based on your destination and preferences."
        else:
            # Show place names only (not IDs) to be user-friendly
            place_list = []
            for i, p in enumerate(found_places[:10], 1):
                place_list.append(f"{i}. {p.get('name', 'Unknown Place')} - {p.get('type', 'place')}")
            
            available_places = "\n".join(place_list)
            error_msg = f"I couldn't find that specific place. Here are the places I found:\n\n{available_places}"
            
            if len(found_places) > 10:
                error_msg += f"\n\n... and {len(found_places) - 10} more places"
            
            error_msg += "\n\nPlease select from these options by number or name."
        
        print(f"⚠️ Place not found: {place_id}")
        
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=error_msg,
                        tool_call_id=tool_call_id
                    )
                ]
            }
        )
    
    # Gather research data
    place_name = place["name"]
    place_type = place.get("type", "place")
    rating = place.get("rating", 0)
    address = place.get('address', 'Unknown')
    
    # Get Wikipedia info
    wiki_info = get_wikipedia_info.invoke(place_name)
    
    # Get weather info (extract city from place name or address)
    location_for_weather = place_name.split(',')[0] if ',' in place_name else place_name
    weather_info = get_weather_info.invoke(location_for_weather)
    
    # Build comprehensive research report
    research_report = f"""
### Research Report: {place_name}

**Type**: {place_type.capitalize()}
**Location**: {address}
**Rating**: {rating}/5.0 ⭐

{wiki_info}

{weather_info}

**Visitor Information**:
- Google Rating: {rating}/5.0
- Category: {place_type}
- Types: {', '.join(place.get('types', [])[:5])}

**Travel Tips**:
- Book accommodations in advance if staying nearby
- Check local opening hours and seasonal closures
- Consider visiting during off-peak hours for better experience
- Research local customs and dress codes if visiting religious/cultural sites

**Estimated Visit Cost**: ${PRICE_MAP.get(place.get('price_level', 'UNSPECIFIED'), 150)}
"""
    
    # Add to researched_places
    new_researched_place = {
        "id": place_id,
        "name": place_name,
        "type": place_type,
        "address": address,
        "rating": rating,
        "report": research_report,
        "estimated_cost": PRICE_MAP.get(place.get('price_level', 'UNSPECIFIED'), 150),
        "lat": place.get("lat", 0),
        "lng": place.get("lng", 0)
    }
    
    return Command(
        update={
            "researched_places": [new_researched_place],
            "research_notes": [research_report],
            "messages": [
                ToolMessage(
                    content=f"✅ Completed comprehensive research for {place_name}. Includes Wikipedia info, weather data, and travel tips.",
                    tool_call_id=tool_call_id
                )
            ]
        }
    )

@tool
def search_flights(origin: str, destination: str) -> str:
    """
    Search for flights between two cities.
    """
    import random
    
    airlines = ["Delta", "United", "British Airways", "JAL", "Emirates"]
    results = []
    
    base_price = 400 if origin != destination else 0
    
    for i in range(3):
        airline = random.choice(airlines)
        price = base_price + random.randint(50, 500)
        flight_num = f"{airline[:2].upper()}{random.randint(100, 999)}"
        
        results.append(
            f"- Flight: {flight_num} ({airline})\n  Route: {origin} -> {destination}\n  Price: ${price}\n  Time: {random.randint(6, 20)}:00"
        )
        
    return "\n".join(results)

@tool
def book_flight(
    flight_number: str, 
    price: float, 
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """
    Book a flight. Verification of funds happens BEFORE booking.
    """
    current_balance = state.get("remaining_budget", 0)
    
    if price > current_balance:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error: Transaction Declined. Cost ${price} exceeds remaining budget of ${current_balance}.",
                        tool_call_id=tool_call_id
                    )
                ]
            }
        )

    new_balance = current_balance - price
    print(f"✈️ FLIGHT BOOKED: {flight_number} for ${price}. New Balance: ${new_balance}")

    return Command(
        update={
            "itinerary": [{
                "name": f"Flight {flight_number}",
                "cost": price,
                "type": "flight",
                "status": "confirmed"
            }],
            "messages": [
                ToolMessage(
                    content=f"Successfully booked Flight {flight_number}. Cost: ${price}. Remaining Budget: ${new_balance}",
                    tool_call_id=tool_call_id
                )
            ]
        }
    )