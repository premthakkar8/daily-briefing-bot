"""
Configuration management for the Daily Briefing Bot
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Configuration class for API keys and settings"""
    
    # Weather API (Open-Meteo - Free, no API key required)
    weather_city: str = "Surat"
    weather_units: str = "metric"  # metric, imperial
    
    # News API
    news_api_key: Optional[str] = None
    news_country: str = "us"
    news_category: str = "general"  # business, entertainment, general, health, science, sports, technology
    
    # Stock API (Alpha Vantage)
    stock_api_key: Optional[str] = None
    stock_symbols: list = None
    
    # Email notifications
    email_enabled: bool = False
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_from: Optional[str] = None
    email_password: Optional[str] = None
    email_to: Optional[str] = None
    
    # Discord webhook (alternative notification)
    discord_webhook_url: Optional[str] = None
    
    # Slack webhook (alternative notification)
    slack_webhook_url: Optional[str] = None
    
    # Calendar integration
    calendar_enabled: bool = False
    calendar_type: str = "google"  # google, outlook
    
    def __post_init__(self):
        """Load configuration from environment variables"""
        # Try to load .env file explicitly
        from pathlib import Path
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        
        self.weather_city = os.getenv("WEATHER_CITY", self.weather_city)
        
        self.news_api_key = os.getenv("NEWS_API_KEY", self.news_api_key)
        self.news_country = os.getenv("NEWS_COUNTRY", self.news_country)
        
        self.stock_api_key = os.getenv("STOCK_API_KEY", self.stock_api_key)
        stock_symbols_env = os.getenv("STOCK_SYMBOLS", "AAPL,GOOGL,MSFT,TSLA")
        self.stock_symbols = stock_symbols_env.split(",") if stock_symbols_env else ["AAPL", "GOOGL", "MSFT", "TSLA"]
        
        self.email_from = os.getenv("EMAIL_FROM", self.email_from)
        self.email_password = os.getenv("EMAIL_PASSWORD", self.email_password)
        self.email_to = os.getenv("EMAIL_TO", self.email_to)
        
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", self.discord_webhook_url)
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", self.slack_webhook_url)
        
        # Enable email if credentials are provided
        if self.email_from and self.email_password and self.email_to:
            self.email_enabled = True
    
    def validate(self) -> bool:
        """Validate that required API keys are present"""
        missing_keys = []
        
        # Weather API is free, no key needed
        
        if not self.news_api_key:
            missing_keys.append("NEWS_API_KEY")
        
        if not self.stock_api_key:
            missing_keys.append("STOCK_API_KEY")
        
        if missing_keys:
            print(f"Warning: Missing API keys: {', '.join(missing_keys)}")
            print("Some features may not work properly.")
            return False
        
        return True
