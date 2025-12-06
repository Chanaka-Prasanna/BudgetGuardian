from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from tools import search_hotels, book_hotel, search_flights, book_flight
from state import TravelState

# 1. Setup LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

# 2. Define Helper to Create Agents
def create_agent(llm, tools, system_prompt: str):
    """Creates a standard ReAct agent."""
    return create_react_agent(llm, tools, prompt=system_prompt)

# 3. Define the Specialized Agents (Workers)

# --- Hotel Scout ---
hotel_agent = create_agent(
    llm, 
    [search_hotels, book_hotel], 
    system_prompt="""You are a Hotel Scout.
    Your job is to find and book hotels based on the user's needs and budget.
    Always check the remaining budget before booking.
    Use the 'search_hotels' tool to find options.
    Use the 'book_hotel' tool to finalize a booking.
    """
)

def hotel_node(state: TravelState) -> dict:
    """Entry point for the Hotel Agent."""
    result = hotel_agent.invoke(state)
    # We return the updated messages. 
    # The state update for budget/itinerary happens inside the tools via Command()
    return {"messages": result["messages"]}


# --- Flight Specialist ---
flight_agent = create_agent(
    llm, 
    [search_flights, book_flight], 
    system_prompt="""You are a Flight Specialist.
    Your job is to find and book flights.
    Always check the remaining budget before booking.
    Use 'search_flights' to find options.
    Use 'book_flight' to finalize.
    """
)

def flight_node(state: TravelState) -> dict:
    """Entry point for the Flight Agent."""
    result = flight_agent.invoke(state)
    return {"messages": result["messages"]}


# 4. Define the Supervisor (Manager)

members = ["Hotel_Scout", "Flight_Specialist"]
system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    " following workers: {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."
)

# The supervisor is an LLM that outputs a structured decision
options = ["FINISH"] + members

# We use function calling (structured output) to force the LLM to choose a valid next step
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
