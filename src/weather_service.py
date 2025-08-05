"""
Weather Service - Fetches weather data using Open-Meteo API (free, no API key required)
"""

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import asyncio
import concurrent.futures

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching weather data using Open-Meteo API"""
    
    def __init__(self, config):
        self.config = config
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)
        
        # Default coordinates (can be overridden by config)
        self.coordinates = self._get_city_coordinates(self.config.weather_city)
    
    def _get_city_coordinates(self, city: str) -> tuple:
        """Get coordinates for major cities (can be expanded)"""
        city_coords = {
            "new york": (40.7128, -74.0060),
            "london": (51.5074, -0.1278),
            "tokyo": (35.6762, 139.6503),
            "paris": (48.8566, 2.3522),
            "sydney": (-33.8688, 151.2093),
            "mumbai": (19.0760, 72.8777),
            "delhi": (28.7041, 77.1025),
            "los angeles": (34.0522, -118.2437),
            "chicago": (41.8781, -87.6298),
            "toronto": (43.6532, -79.3832),
            "berlin": (52.5200, 13.4050),
            "moscow": (55.7558, 37.6176),
            "beijing": (39.9042, 116.4074),
            "seoul": (37.5665, 126.9780),
            "bangkok": (13.7563, 100.5018),
            "singapore": (1.3521, 103.8198),
            "dubai": (25.2048, 55.2708),
            "cairo": (30.0444, 31.2357),
            "johannesburg": (-26.2041, 28.0473),
            "buenos aires": (-34.6118, -58.3960),
            "surat": (21.1959, 72.8302)  # Your provided coordinates
        }
        
        city_lower = city.lower()
        return city_coords.get(city_lower, (40.7128, -74.0060))  # Default to NYC
    
    async def get_weather(self) -> Dict[str, Any]:
        """Get current weather and forecast"""
        try:
            # Run the synchronous Open-Meteo call in a thread pool
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(executor, self._fetch_weather_data)
            
            return self._parse_weather_response(response)
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            raise
    
    def _fetch_weather_data(self):
        """Fetch weather data from Open-Meteo API (synchronous)"""
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.coordinates[0],
            "longitude": self.coordinates[1],
            "daily": ["sunrise", "sunset", "temperature_2m_min", "temperature_2m_max", 
                     "rain_sum", "weather_code"],
            "hourly": ["temperature_2m", "rain", "weather_code", "wind_speed_10m"],
            "current": ["temperature_2m", "apparent_temperature", "rain", "weather_code", 
                       "wind_speed_10m", "relative_humidity_2m"],
            "timezone": "auto",
            "temperature_unit": "celsius" if self.config.weather_units == "metric" else "fahrenheit"
        }
        
        responses = self.openmeteo.weather_api(url, params=params)
        return responses[0]  # Process first location
    
    def _parse_weather_response(self, response) -> Dict[str, Any]:
        """Parse Open-Meteo response into our format"""
        # Current weather
        current = response.Current()
        current_temp = current.Variables(0).Value()
        apparent_temp = current.Variables(1).Value()
        current_rain = current.Variables(2).Value()
        weather_code = int(current.Variables(3).Value())
        wind_speed = current.Variables(4).Value()
        humidity = current.Variables(5).Value()
        
        unit_symbol = "°C" if self.config.weather_units == "metric" else "°F"
        wind_unit = "m/s" if self.config.weather_units == "metric" else "mph"
        
        current_weather = {
            "temperature": f"{current_temp:.1f}{unit_symbol}",
            "feels_like": f"{apparent_temp:.1f}{unit_symbol}",
            "humidity": f"{humidity:.0f}%",
            "description": self._get_weather_description(weather_code),
            "wind_speed": f"{wind_speed:.1f} {wind_unit}",
            "rain": f"{current_rain:.1f} mm" if current_rain > 0 else "No rain",
            "icon": self._get_weather_icon(weather_code)
        }
        
        # Hourly forecast (next 12 hours)
        hourly = response.Hourly()
        hourly_temp = hourly.Variables(0).ValuesAsNumpy()
        hourly_rain = hourly.Variables(1).ValuesAsNumpy()
        hourly_weather_codes = hourly.Variables(2).ValuesAsNumpy()
        
        hourly_data = pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )
        
        forecast = []
        for i in range(min(4, len(hourly_data))):  # Next 4 data points (12 hours)
            forecast.append({
                "time": hourly_data[i].strftime("%H:%M"),
                "temperature": f"{hourly_temp[i]:.1f}{unit_symbol}",
                "description": self._get_weather_description(int(hourly_weather_codes[i])),
                "rain": f"{hourly_rain[i]:.1f}mm" if hourly_rain[i] > 0 else "No rain",
                "icon": self._get_weather_icon(int(hourly_weather_codes[i]))
            })
        
        # Daily data for additional info
        daily = response.Daily()
        daily_min_temp = daily.Variables(2).ValuesAsNumpy()
        daily_max_temp = daily.Variables(3).ValuesAsNumpy()
        
        return {
            "current": current_weather,
            "forecast": forecast,
            "city": self.config.weather_city,
            "coordinates": f"{response.Latitude():.2f}°N {response.Longitude():.2f}°E",
            "today_high": f"{daily_max_temp[0]:.1f}{unit_symbol}",
            "today_low": f"{daily_min_temp[0]:.1f}{unit_symbol}",
            "timezone": f"{response.Timezone()} {response.TimezoneAbbreviation()}"
        }
    
    def _get_weather_description(self, weather_code: int) -> str:
        """Convert WMO weather code to description"""
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(weather_code, "Unknown")
    
    def _get_weather_icon(self, weather_code: int) -> str:
        """Get emoji icon for weather code"""
        if weather_code == 0:
            return "☀️"
        elif weather_code in [1, 2]:
            return "⛅"
        elif weather_code == 3:
            return "☁️"
        elif weather_code in [45, 48]:
            return "🌫️"
        elif weather_code in [51, 53, 55, 56, 57]:
            return "🌦️"
        elif weather_code in [61, 63, 65, 66, 67, 80, 81, 82]:
            return "🌧️"
        elif weather_code in [71, 73, 75, 77, 85, 86]:
            return "🌨️"
        elif weather_code in [95, 96, 99]:
            return "⛈️"
        else:
            return "🌤️"
