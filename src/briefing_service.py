"""
Briefing Service - Coordinates all data collection for the daily briefing
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from .weather_service import WeatherService
from .news_service import NewsService
from .stock_service import StockService
from .calendar_service import CalendarService

logger = logging.getLogger(__name__)


class BriefingService:
    """Service to coordinate all briefing data collection"""
    
    def __init__(self, config):
        self.config = config
        self.weather_service = WeatherService(config)
        self.news_service = NewsService(config)
        self.stock_service = StockService(config)
        self.calendar_service = CalendarService(config)
    
    async def get_full_briefing(self) -> Dict[str, Any]:
        """Get all briefing data asynchronously"""
        briefing_data = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%A, %B %d, %Y"),
            "weather": None,
            "news": None,
            "stocks": None,
            "calendar": None,
            "errors": []
        }
        
        # Collect all data concurrently
        tasks = []
        
        # Weather (Open-Meteo is free, always available)
        tasks.append(self._get_weather_safe())
        
        # News
        if self.config.news_api_key:
            tasks.append(self._get_news_safe())
        else:
            briefing_data["errors"].append("News: API key not configured")
        
        # Stocks
        if self.config.stock_api_key:
            tasks.append(self._get_stocks_safe())
        else:
            briefing_data["errors"].append("Stocks: API key not configured")
        
        # Calendar
        if self.config.calendar_enabled:
            tasks.append(self._get_calendar_safe())
        
        # Execute all tasks
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            result_index = 0
            
            # Weather is always first
            briefing_data["weather"] = results[result_index]
            result_index += 1
            
            if self.config.news_api_key:
                briefing_data["news"] = results[result_index]
                result_index += 1
            
            if self.config.stock_api_key:
                briefing_data["stocks"] = results[result_index]
                result_index += 1
            
            if self.config.calendar_enabled:
                briefing_data["calendar"] = results[result_index]
        
        return briefing_data
    
    async def _get_weather_safe(self):
        """Safely get weather data"""
        try:
            return await self.weather_service.get_weather()
        except Exception as e:
            logger.error(f"Weather service error: {e}")
            return {"error": str(e)}
    
    async def _get_news_safe(self):
        """Safely get news data"""
        try:
            return await self.news_service.get_top_headlines()
        except Exception as e:
            logger.error(f"News service error: {e}")
            return {"error": str(e)}
    
    async def _get_stocks_safe(self):
        """Safely get stock data"""
        try:
            return await self.stock_service.get_stock_prices()
        except Exception as e:
            logger.error(f"Stock service error: {e}")
            return {"error": str(e)}
    
    async def _get_calendar_safe(self):
        """Safely get calendar data"""
        try:
            return await self.calendar_service.get_today_events()
        except Exception as e:
            logger.error(f"Calendar service error: {e}")
            return {"error": str(e)}
