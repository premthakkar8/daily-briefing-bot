#!/usr/bin/env python3
"""
Test script for the Daily Briefing Bot
Run this to test your configuration and see a sample briefing
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from src.briefing_service import BriefingService
from src.config import Config
from src.notifier import Notifier

# Load environment variables from .env file
load_dotenv()

# Configure logging for testing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_briefing():
    """Test the briefing system"""
    print("Testing Daily Briefing Bot...")
    print("=" * 50)
    
    # Initialize services
    config = Config()
    
    # Validate configuration
    if not config.validate():
        print("\n⚠️ Some API keys are missing. The briefing will show limited data.")
        print("Check the README.md for instructions on getting API keys.")
    
    print(f"\nConfiguration:")
    print(f"Weather City: {config.weather_city}")
    print(f"News Country: {config.news_country}")
    print(f"News Category: {config.news_category}")
    print(f"Stock Symbols: {config.stock_symbols}")
    print(f"Email Enabled: {config.email_enabled}")
    print("=" * 50)
    
    # Generate briefing
    briefing_service = BriefingService(config)
    notifier = Notifier(config)
    
    try:
        print("\nGenerating briefing...")
        briefing_data = await briefing_service.get_full_briefing()
        
        print("Sending briefing...")
        await notifier.send_briefing(briefing_data)
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logging.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_briefing())
