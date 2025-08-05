"""
Notification Service - Handles sending briefings via various channels
"""

import logging
import smtplib
import aiohttp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any

logger = logging.getLogger(__name__)


class Notifier:
    """Service for sending notifications"""
    
    def __init__(self, config):
        self.config = config
    
    async def send_briefing(self, briefing_data: Dict[str, Any]):
        """Send briefing through all configured channels"""
        message = self._format_briefing_message(briefing_data)
        
        # Send via email if configured
        if self.config.email_enabled:
            try:
                await self._send_email(message, briefing_data)
                logger.info("Briefing sent via email")
            except Exception as e:
                logger.error(f"Failed to send email: {e}")
        
        # Send via Discord if configured
        if self.config.discord_webhook_url:
            try:
                await self._send_discord_message(message)
                logger.info("Briefing sent via Discord")
            except Exception as e:
                logger.error(f"Failed to send Discord message: {e}")
        
        # Send via Slack if configured
        if self.config.slack_webhook_url:
            try:
                await self._send_slack_message(message)
                logger.info("Briefing sent via Slack")
            except Exception as e:
                logger.error(f"Failed to send Slack message: {e}")
        
        # Always log to console
        print("=" * 60)
        print("DAILY BRIEFING")
        print("=" * 60)
        print(message)
        print("=" * 60)
    
    def _format_briefing_message(self, briefing_data: Dict[str, Any]) -> str:
        """Format briefing data into a readable message"""
        message_parts = []
        
        # Header
        message_parts.append(f"📋 Daily Briefing for {briefing_data.get('date', 'Today')}")
        message_parts.append("")
        
        # Weather section
        weather = briefing_data.get("weather")
        if weather and "error" not in weather:
            message_parts.append("🌤️ WEATHER")
            message_parts.append("-" * 20)
            current = weather.get("current", {})
            message_parts.append(f"📍 {weather.get('city', 'N/A')} ({weather.get('coordinates', 'N/A')})")
            message_parts.append(f"🌡️ {current.get('temperature', 'N/A')} (feels like {current.get('feels_like', 'N/A')})")
            message_parts.append(f"📊 High: {weather.get('today_high', 'N/A')} | Low: {weather.get('today_low', 'N/A')}")
            message_parts.append(f"{current.get('icon', '')} {current.get('description', 'N/A')}")
            message_parts.append(f"💨 Wind: {current.get('wind_speed', 'N/A')}")
            message_parts.append(f"💧 Humidity: {current.get('humidity', 'N/A')}")
            if current.get('rain') != "No rain":
                message_parts.append(f"🌧️ Rain: {current.get('rain', 'N/A')}")
            message_parts.append("")
            
            # Forecast
            forecast = weather.get("forecast", [])
            if forecast:
                message_parts.append("📈 Next 12 Hours:")
                for item in forecast:
                    time_str = item.get("time", "")
                    rain_info = f" | {item.get('rain', '')}" if item.get('rain') != "No rain" else ""
                    message_parts.append(f"  {time_str}: {item.get('temperature', 'N/A')} - {item.get('description', 'N/A')}{rain_info}")
            message_parts.append("")
        
        # News section
        news = briefing_data.get("news")
        if news and "error" not in news:
            message_parts.append("📰 NEWS HIGHLIGHTS")
            message_parts.append("-" * 20)
            articles = news.get("articles", [])
            for i, article in enumerate(articles, 1):
                message_parts.append(f"{i}. {article.get('title', 'No title')}")
                message_parts.append(f"   Source: {article.get('source', 'Unknown')}")
                if article.get('description'):
                    desc = article['description'][:100] + "..." if len(article['description']) > 100 else article['description']
                    message_parts.append(f"   {desc}")
                message_parts.append("")
        
        # Stocks section
        stocks = briefing_data.get("stocks")
        if stocks and "error" not in stocks:
            message_parts.append("📈 STOCK PRICES")
            message_parts.append("-" * 20)
            stock_list = stocks.get("stocks", [])
            for stock in stock_list:
                if "error" not in stock:
                    symbol = stock.get("symbol", "N/A")
                    price = stock.get("price", "N/A")
                    change = stock.get("change", "N/A")
                    change_percent = stock.get("change_percent", "N/A")
                    emoji = "📈" if stock.get("is_positive", False) else "📉"
                    message_parts.append(f"{emoji} {symbol}: {price} ({change}, {change_percent})")
            message_parts.append("")
        
        # Calendar section
        calendar_data = briefing_data.get("calendar")
        if calendar_data and calendar_data.get("enabled") and "error" not in calendar_data:
            message_parts.append("📅 TODAY'S SCHEDULE")
            message_parts.append("-" * 20)
            events = calendar_data.get("events", [])
            if events:
                for event in events:
                    title = event.get("title", "No title")
                    time_str = event.get("time", "")
                    location = event.get("location", "")
                    location_text = f" @ {location}" if location else ""
                    message_parts.append(f"🕐 {time_str}: {title}{location_text}")
            else:
                message_parts.append("No events scheduled for today")
            message_parts.append("")
        
        # Errors section
        errors = briefing_data.get("errors", [])
        if errors:
            message_parts.append("⚠️ NOTES")
            message_parts.append("-" * 20)
            for error in errors:
                message_parts.append(f"• {error}")
            message_parts.append("")
        
        return "\n".join(message_parts)
    
    async def _send_email(self, message: str, briefing_data: Dict[str, Any]):
        """Send briefing via email"""
        msg = MIMEMultipart()
        msg['From'] = self.config.email_from
        msg['To'] = self.config.email_to
        msg['Subject'] = f"Daily Briefing - {briefing_data.get('date', 'Today')}"
        
        msg.attach(MIMEText(message, 'plain'))
        
        with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
            server.starttls()
            server.login(self.config.email_from, self.config.email_password)
            server.send_message(msg)
    
    async def _send_discord_message(self, message: str):
        """Send briefing via Discord webhook"""
        payload = {
            "content": f"```\n{message}\n```"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.config.discord_webhook_url, json=payload) as response:
                if response.status not in [200, 204]:
                    error_text = await response.text()
                    raise Exception(f"Discord webhook error: {response.status} - {error_text}")
    
    async def _send_slack_message(self, message: str):
        """Send briefing via Slack webhook"""
        payload = {
            "text": f"```{message}```"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.config.slack_webhook_url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Slack webhook error: {response.status} - {error_text}")
