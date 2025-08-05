#!/usr/bin/env python3
"""
Daily Briefing Bot - Main Application
Automatically provides daily briefings with weather, news, stocks, and calendar events
"""

import asyncio
import logging
from datetime import datetime, time
from typing import Dict, Any
import schedule
import time as time_module
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.briefing_service import BriefingService
from src.config import Config
from src.notifier import Notifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('briefing_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class DailyBriefingBot:
    """Main class for the Daily Briefing Bot"""
    
    def __init__(self):
        self.config = Config()
        self.briefing_service = BriefingService(self.config)
        self.notifier = Notifier(self.config)
        
    async def generate_daily_briefing(self) -> Dict[str, Any]:
        """Generate the complete daily briefing"""
        logger.info("Generating daily briefing...")
        
        try:
            briefing_data = await self.briefing_service.get_full_briefing()
            return briefing_data
        except Exception as e:
            logger.error(f"Error generating briefing: {e}")
            return {"error": str(e)}
    
    async def send_briefing(self):
        """Generate and send the daily briefing"""
        briefing_data = await self.generate_daily_briefing()
        
        if "error" not in briefing_data:
            await self.notifier.send_briefing(briefing_data)
            logger.info("Daily briefing sent successfully")
        else:
            logger.error(f"Failed to send briefing: {briefing_data['error']}")
    
    def schedule_briefings(self):
        """Schedule the daily briefing jobs"""
        # Schedule for 8:00 AM daily
        schedule.every().day.at("08:00").do(
            lambda: asyncio.run(self.send_briefing())
        )
        
        # You can add more scheduled times here
        # schedule.every().day.at("18:00").do(lambda: asyncio.run(self.send_briefing()))
        
        logger.info("Briefing scheduled for 8:00 AM daily")
    
    def run(self):
        """Start the bot and keep it running"""
        logger.info("Starting Daily Briefing Bot...")
        
        # Schedule the briefings
        self.schedule_briefings()
        
        # Keep the bot running
        while True:
            schedule.run_pending()
            time_module.sleep(60)  # Check every minute


def main():
    """Main entry point"""
    bot = DailyBriefingBot()
    
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")


if __name__ == "__main__":
    main()
