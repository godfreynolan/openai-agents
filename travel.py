import os
import asyncio
from agents import Agent, Runner, function_tool
from amadeus import Client, ResponseError
from dotenv import load_dotenv
load_dotenv()

amadeus = Client(
    client_id=os.getenv("AMADEUS_CLIENT_ID"),
    client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
)

@function_tool
def get_flight(city: str) -> str:
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode='DTW',
        destinationLocationCode='IAH',
        departureDate='2025-05-19',
        adults=1)
    first_offer = response.data[0]  # Get the first flight result
    return {
            "carrier": first_offer['validatingAirlineCodes'][0],
            "departure": first_offer['itineraries'][0]['segments'][0]['departure']['at'],
            "arrival": first_offer['itineraries'][0]['segments'][1]['arrival']['at'],
            "duration": first_offer['itineraries'][0]['duration'],
            "cost": first_offer['price']['grandTotal']
    }


@function_tool
def get_hotel(city: str) -> str:
    response = amadeus.reference_data.locations.hotels.by_city.get(cityCode='PAR')
    # print(response.data[0])
    return {
        "hotelName": response.data[0]['chainCode'], 
        "hotelAddress": response.data[0]['name']
    }   


agent = Agent(
    name="Travel agent",
    instructions="You can only provide flights and hotel information.",
    tools=[get_hotel, get_flight],
)

hotel_agent = Agent(
    name="Hotel agent",
    instructions="You are a helpful hotel booking assitant only. You know nothing about flight information.",
    tools=[get_hotel]
)

airline_agent = Agent(
    name="Airline agent",
    instructions="You only a helpful flight assistant. You know nothing about booking hotels.",
    tools=[get_flight]
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the whether they want flight information or hotel booking information",
    handoffs=[airline_agent, hotel_agent]
)


async def main():
    #result = await Runner.run(triage_agent, input="Please can you give me flight information from Detroit to Houston?")
    result = await Runner.run(triage_agent, input="Where can I stay in Paris?")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
