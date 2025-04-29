import asyncio
import requests
import os
from agents import Agent, Runner, function_tool


@function_tool
def get_weather(city: str) -> str:
    api_key = os.getenv("WEATHER_API_KEY")
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=imperial"
    )
    resp = requests.get(url)
    # print(f"weather data from {url} is {resp}")
    data = resp.json()
    return {
        "city": data["name"],
        "temp_celsius": data["main"]["temp"],
        "conditions": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
    }



agent = Agent(
    name="Weather agent",
    instructions="You can only provide weather information.",
    tools=[get_weather],
)

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
    tools=[get_weather]
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
    tools=[get_weather]
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent]
)


async def main():
    result = await Runner.run(triage_agent, input="Hola, ¿cómo estás? ¿Puedes darme el clima para Detroit?")
    # result = await Runner.run(triage_agent, input="What is the weather like in Detroit?")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
