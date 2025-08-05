"""
News Service - Fetches news headlines using News API
"""

import aiohttp
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class NewsService:
    """Service for fetching news headlines"""
    
    def __init__(self, config):
        self.config = config
        self.base_url = "https://newsapi.org/v2"
    
    async def get_top_headlines(self) -> Dict[str, Any]:
        """Get top news headlines"""
        if not self.config.news_api_key:
            raise ValueError("News API key not configured")
        
        url = f"{self.base_url}/top-headlines"
        headers = {
            "X-API-Key": self.config.news_api_key
        }
        params = {
            "country": self.config.news_country,
            "category": self.config.news_category,
            "pageSize": 10  # Get top 10 headlines
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_news_data(data)
                else:
                    error_text = await response.text()
                    raise Exception(f"News API error: {response.status} - {error_text}")
    
    def _parse_news_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse news API response"""
        articles = data.get("articles", [])
        
        parsed_articles = []
        for article in articles[:5]:  # Top 5 headlines
            parsed_articles.append({
                "title": article.get("title", "No title"),
                "description": article.get("description", "No description"),
                "source": article.get("source", {}).get("name", "Unknown"),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", ""),
                "author": article.get("author", "Unknown")
            })
        
        return {
            "total_results": data.get("totalResults", 0),
            "articles": parsed_articles,
            "category": self.config.news_category.title(),
            "country": self.config.news_country.upper()
        }
