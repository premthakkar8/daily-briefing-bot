# Daily Briefing Bot 🤖

An automated Python bot that delivers personalized daily briefings with weather, news headlines, stock prices, and calendar events via email and console output.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Features

- 🌤️ **Weather Updates**: Real-time weather data for any city using Open-Meteo API (free!)
- 📰 **News Headlines**: Top news stories using News API
- 📈 **Stock Prices**: Real-time stock prices using Alpha Vantage API
- 📅 **Calendar Events**: Daily schedule (currently mock, extensible to Google/Outlook)
- ⏰ **Scheduled Delivery**: Automatic daily briefings at specified times (default: 8:00 AM)
- 📧 **Multi-Channel Notifications**: Email, Discord, Slack, and console output
- 🔄 **Async Operations**: Fast, concurrent API calls for optimal performance

## 📋 Sample Output

```
============================================================
DAILY BRIEFING
============================================================
📋 Daily Briefing for Tuesday, August 05, 2025

🌤️ WEATHER
--------------------
📍 Surat (21.25°N 72.88°E)
🌡️ 27.6°C (feels like 32.6°C)
📊 High: 30.7°C | Low: 26.0°C
⛅ Mainly clear
💨 Wind: 9.5 m/s
💧 Humidity: 83%

📰 NEWS HIGHLIGHTS
--------------------
1. Tech Giant Announces Revolutionary AI Breakthrough
2. Global Climate Summit Reaches Historic Agreement
...

📈 STOCK PRICES
--------------------
📈 AAPL: $203.35 ($+0.97, +0.48%)
📈 META: $776.37 ($+26.36, +3.51%)
📈 NVDA: $180.00 ($+6.28, +3.62%)
...
============================================================
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- API keys (see Configuration section)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/daily-briefing-bot.git
   cd daily-briefing-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (see Configuration section)
   ```

## ⚙️ Configuration

### Required API Keys

Get free API keys from:

- **News API**: https://newsapi.org/ (Free: 1,000 requests/day)
- **Alpha Vantage**: https://www.alphavantage.co/support/#api-key (Free: 5 requests/minute)

### Environment Variables

Create a `.env` file in the project root:

```env
# Required API Keys
NEWS_API_KEY=your_news_api_key
STOCK_API_KEY=your_alphavantage_api_key

# Optional Configuration
WEATHER_CITY=Surat
NEWS_COUNTRY=us
NEWS_CATEGORY=technology
STOCK_SYMBOLS=AAPL,META,NVDA,GOOGL,TSLA

# Email Notifications (optional)
EMAIL_FROM=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=recipient@gmail.com

# Webhook Notifications (optional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### Configuration Options

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `WEATHER_CITY` | City for weather data | "New York" | Any major city |
| `NEWS_COUNTRY` | Country for news | "us" | us, uk, in, ca, etc. |
| `NEWS_CATEGORY` | News category | "general" | business, technology, health, science, sports |
| `STOCK_SYMBOLS` | Stock symbols to track | "AAPL,GOOGL,MSFT,TSLA" | Comma-separated list |

## 🚀 Usage

### Test the Bot

```bash
python test_briefing.py
```

### Run Scheduled Bot

```bash
python main.py
```

The bot will run continuously and send briefings at 8:00 AM daily.

### Customize Schedule

Edit `main.py` to add more briefing times:

```python
def schedule_briefings(self):
    schedule.every().day.at("08:00").do(lambda: asyncio.run(self.send_briefing()))
    schedule.every().day.at("18:00").do(lambda: asyncio.run(self.send_briefing()))  # Evening briefing
```

## 📁 Project Structure

```
daily-briefing-bot/
├── main.py                 # Main application entry point
├── test_briefing.py        # Test script for manual briefing
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── README.md              # This file
└── src/
    ├── __init__.py
    ├── config.py          # Configuration management
    ├── briefing_service.py # Main briefing coordinator
    ├── weather_service.py  # Weather data (Open-Meteo API)
    ├── news_service.py     # News headlines (News API)
    ├── stock_service.py    # Stock prices (Alpha Vantage API)
    ├── calendar_service.py # Calendar events (mock/extensible)
    └── notifier.py         # Multi-channel notifications
```

## 🔧 Development

### Adding New Data Sources

1. Create a new service class in `src/`
2. Add to `BriefingService` in `src/briefing_service.py`
3. Update message formatting in `src/notifier.py`

### Adding Real Calendar Integration

Uncomment and install calendar dependencies in `requirements.txt`:

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
# or
pip install msal  # for Microsoft Graph API
```

## 🌐 Deployment

### Local Deployment
- Keep your computer running for scheduled briefings
- Set up Windows Task Scheduler for auto-start

### Cloud Deployment
Deploy to platforms like:
- **Heroku** (free tier available)
- **Railway**
- **Render**
- **Google Cloud Run**
- **AWS Lambda**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Important Notes

- Never commit your `.env` file with real API keys
- Free API tiers have rate limits - upgrade for higher usage
- For Gmail notifications, use app-specific passwords
- Some Indian stocks may not be available in Alpha Vantage free tier

## 🙏 Acknowledgments

- [Open-Meteo](https://open-meteo.com/) for free weather data
- [News API](https://newsapi.org/) for news headlines
- [Alpha Vantage](https://www.alphavantage.co/) for stock market data

---

⭐ **Star this repo if you found it helpful!**
