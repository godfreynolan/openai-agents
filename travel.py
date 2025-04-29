# set up travel agent with a function tool to get travel information and a function tool to get car hire information
# add in the API calls to get the information
# use the code in helloworld 
# add a guardrail

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
def get_carhire(city: str) -> str:
    response = amadeus.shopping.car_rental_offers.get(
        pickupLocationCode='IAH',
        pickupDateTime='2025-05-19T10:00:00',
        returnDateTime='2025-05-22T18:00:00',
    )
    offers = response.data
    print(offers[0])
    return {
        "city": city,
        "carHire": "Enterprise car hire rental at Houston airport",
        "description": "Car hire details, including price and availability - $99 per day",
    }


agent = Agent(
    name="Travel agent",
    instructions="You can only provide flights and car rental information.",
    tools=[get_carhire, get_flight],
)

carhire_agent = Agent(
    name="Car Rental agent",
    instructions="You are a helpful care rental assitant only. You know nothing about flight information.",
    tools=[get_carhire]
)

airline_agent = Agent(
    name="Airline agent",
    instructions="You only a helpful flight assistant. You know nothing about car rental information.",
    tools=[get_flight]
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the whether they want flight information or car rental information",
    handoffs=[airline_agent, carhire_agent]
)


async def main():
    result = await Runner.run(triage_agent, input="Please can you give me flight information from Detroit to Houston?")
    #result = await Runner.run(triage_agent, input="Please can you give me information about renting a car in Houston?")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
