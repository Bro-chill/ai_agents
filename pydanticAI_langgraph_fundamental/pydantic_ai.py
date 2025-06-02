from __future__ import annotations as _annotations

import asyncio
import os
import urllib.parse
from dataclasses import dataclass
from typing import Any

import logfire
from devtools import debug
from httpx import AsyncClient
from pydantic import BaseModel

from pydantic_ai import Agent, ModelRetry, RunContext, ModelSettings, UsageLimit

# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_pydantic_ai()


@dataclass
class Deps:
    """External dependencies for the weather agent."""
    client: AsyncClient
    weather_api_key: str | None
    geo_api_key: str | None


class WeatherResponse(BaseModel):
    """Structured response for weather information."""
    summary: str
    locations: list[dict[str, Any]]
    temperature_unit: str = "Celsius"


# System prompt that guides the model's behavior
system_prompt = """
You are a helpful weather assistant. Your role is to:
1. Provide accurate weather information for requested locations
2. Be concise and informative in your responses
3. Always use the provided tools to get real-time data
4. Format responses in a friendly, conversational tone
5. Include temperature and weather conditions for each location
6. If multiple locations are requested, compare them briefly

Always use the get_lat_lng tool first to get coordinates, then use get_weather tool for each location.
"""

# Model settings for controlling behavior
model_settings = ModelSettings(
    max_tokens=500,           # Limit response length
    temperature=0.3,          # Lower creativity for factual responses
    top_p=0.9,               # Focused sampling
    timeout=30.0,            # 30 second timeout
    presence_penalty=0.1,     # Slight penalty for repetition
    frequency_penalty=0.1,    # Slight penalty for frequency
)

# Usage limits
usage_limit = UsageLimit(
    request_limit=100,              # Max 100 requests
    request_tokens_limit=10000,     # Max 10k tokens per request
    response_tokens_limit=2000,     # Max 2k tokens per response
    total_tokens_limit=50000,       # Max 50k total tokens
)

weather_agent = Agent(
    'openai:gpt-4o',
    deps_type=Deps,
    output_type=WeatherResponse,
    system_prompt=system_prompt,
    retries=2,
    model_settings=model_settings,
    usage_limit=usage_limit,
)


@weather_agent.tool
async def get_lat_lng(
    ctx: RunContext[Deps], location_description: str
) -> dict[str, float]:
    """Get the latitude and longitude of a location.

    Args:
        ctx: The context with dependencies.
        location_description: A description of a location.
    """
    if ctx.deps.geo_api_key is None:
        # if no API key is provided, return a dummy response (London)
        return {'lat': 51.1, 'lng': -0.1}

    params = {'access_token': ctx.deps.geo_api_key}
    loc = urllib.parse.quote(location_description)
    r = await ctx.deps.client.get(
        f'https://api.mapbox.com/geocoding/v5/mapbox.places/{loc}.json', params=params
    )
    r.raise_for_status()
    data = r.json()

    if features := data['features']:
        lng, lat = features[0]['center']  # Note: Mapbox returns [lng, lat]
        return {'lat': lat, 'lng': lng}
    else:
        raise ModelRetry('Could not find the location')


@weather_agent.tool
async def get_weather(ctx: RunContext[Deps], lat: float, lng: float) -> dict[str, Any]:
    """Get the weather at a location.

    Args:
        ctx: The context with dependencies.
        lat: Latitude of the location.
        lng: Longitude of the location.
    """
    if ctx.deps.weather_api_key is None:
        # if no API key is provided, return a dummy response
        return {'temperature': '21°C', 'description': 'Sunny', 'location': f'{lat},{lng}'}

    params = {
        'apikey': ctx.deps.weather_api_key,
        'location': f'{lat},{lng}',
        'units': 'metric',
    }
    with logfire.span('calling weather API', params=params) as span:
        r = await ctx.deps.client.get(
            'https://api.tomorrow.io/v4/weather/realtime', params=params
        )
        r.raise_for_status()
        data = r.json()
        span.set_attribute('response', data)

    values = data['data']['values']
    # https://docs.tomorrow.io/reference/data-layers-weather-codes
    code_lookup = {
        1000: 'Clear, Sunny',
        1100: 'Mostly Clear',
        1101: 'Partly Cloudy',
        1102: 'Mostly Cloudy',
        1001: 'Cloudy',
        2000: 'Fog',
        2100: 'Light Fog',
        4000: 'Drizzle',
        4001: 'Rain',
        4200: 'Light Rain',
        4201: 'Heavy Rain',
        5000: 'Snow',
        5001: 'Flurries',
        5100: 'Light Snow',
        5101: 'Heavy Snow',
        6000: 'Freezing Drizzle',
        6001: 'Freezing Rain',
        6200: 'Light Freezing Rain',
        6201: 'Heavy Freezing Rain',
        7000: 'Ice Pellets',
        7101: 'Heavy Ice Pellets',
        7102: 'Light Ice Pellets',
        8000: 'Thunderstorm',
    }
    return {
        'temperature': f'{values["temperatureApparent"]:0.0f}°C',
        'description': code_lookup.get(values['weatherCode'], 'Unknown'),
        'location': f'{lat},{lng}',
        'humidity': values.get('humidity', 'N/A'),
        'wind_speed': f'{values.get("windSpeed", 0):0.1f} m/s'
    }


@weather_agent.tool_plain
def format_temperature(temperature_celsius: float) -> str:
    """Convert temperature to different formats.
    
    This is a plain tool that doesn't need agent context.
    
    Args:
        temperature_celsius: Temperature in Celsius.
    """
    fahrenheit = (temperature_celsius * 9/5) + 32
    return f"{temperature_celsius}°C ({fahrenheit:.1f}°F)"


async def main():
    async with AsyncClient() as client:
        logfire.instrument_httpx(client, capture_all=True)
        # create a free API key at https://www.tomorrow.io/weather-api/
        weather_api_key = os.getenv('WEATHER_API_KEY')
        # create a free API key at https://www.mapbox.com/
        geo_api_key = os.getenv('GEO_API_KEY')
        deps = Deps(
            client=client, 
            weather_api_key=weather_api_key, 
            geo_api_key=geo_api_key
        )
        
        try:
            # Check usage limits before making request
            if weather_agent.usage_limit and weather_agent.usage_limit.has_token_limits():
                print("Token limits are configured")
            
            result = await weather_agent.run(
                'What is the weather like in London and in Wiltshire?', 
                deps=deps
            )
            debug(result)
            print('Response:', result.output)
            
            # Check usage after request
            if weather_agent.usage_limit:
                print(f"Usage info: {result.usage()}")
                
        except Exception as e:
            print(f"Error occurred: {e}")


if __name__ == '__main__':
    asyncio.run(main())