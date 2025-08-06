#!/usr/bin/env python3
"""
GitHub Actions script for sending daily briefings via email
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from src.briefing_service import BriefingService
from src.config import Config
from src.notifier import Notifier

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def send_daily_briefing():
    """Send daily briefing via GitHub Actions"""
    try:
        # Initialize services
        config = Config()
        
        # Debug: Check if environment variables are loaded
        logger.info(f"NEWS_API_KEY configured: {bool(config.news_api_key)}")
        logger.info(f"STOCK_API_KEY configured: {bool(config.stock_api_key)}")
        logger.info(f"EMAIL_FROM configured: {bool(config.email_from)}")
        logger.info(f"EMAIL_TO configured: {bool(config.email_to)}")
        logger.info(f"Email enabled: {config.email_enabled}")
        
        briefing_service = BriefingService(config)
        notifier = Notifier(config)
        
        # Generate briefing
        logger.info("Generating daily briefing...")
        briefing_data = await briefing_service.get_full_briefing()
        
        # Send briefing
        logger.info("Sending daily briefing...")
        await notifier.send_briefing(briefing_data)
        
        # Check if news data exists
        news = briefing_data.get("news")
        if news and "error" not in news:
            articles = news.get("articles", [])
            logger.info(f"News articles found: {len(articles)}")
            if articles:
                logger.info(f"First article: {articles[0].get('title', 'No title')}")
        else:
            logger.warning("No news data or news error")
            if news and "error" in news:
                logger.error(f"News error: {news['error']}")
        
        logger.info("Daily briefing sent successfully!")
        
    except Exception as e:
        logger.error(f"Failed to send daily briefing: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(send_daily_briefing())
