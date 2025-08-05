"""
Stock Service - Fetches stock prices using Alpha Vantage API
"""

import aiohttp
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class StockService:
    """Service for fetching stock market data"""
    
    def __init__(self, config):
        self.config = config
        self.base_url = "https://www.alphavantage.co/query"
    
    async def get_stock_prices(self) -> Dict[str, Any]:
        """Get current stock prices for configured symbols"""
        if not self.config.stock_api_key:
            raise ValueError("Stock API key not configured")
        
        stock_data = []
        
        # Get data for each stock symbol
        for symbol in self.config.stock_symbols:
            try:
                data = await self._get_stock_quote(symbol)
                stock_data.append(data)
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                stock_data.append({
                    "symbol": symbol,
                    "error": str(e)
                })
        
        return {
            "stocks": stock_data,
            "symbols": self.config.stock_symbols
        }
    
    async def _get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get quote for a single stock symbol"""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.config.stock_api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_stock_data(symbol, data)
                else:
                    error_text = await response.text()
                    raise Exception(f"Stock API error for {symbol}: {response.status} - {error_text}")
    
    def _parse_stock_data(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse stock API response"""
        # Check if we have an error response
        if "Error Message" in data:
            raise Exception(f"API Error: {data['Error Message']}")
        
        if "Note" in data:
            raise Exception(f"API Limit: {data['Note']}")
        
        quote_data = data.get("Global Quote", {})
        
        if not quote_data:
            raise Exception("No quote data returned")
        
        # Parse the quote data
        try:
            price = float(quote_data.get("05. price", 0))
            change = float(quote_data.get("09. change", 0))
            change_percent = quote_data.get("10. change percent", "0%").replace("%", "")
            change_percent = float(change_percent)
            
            return {
                "symbol": symbol,
                "price": f"${price:.2f}",
                "change": f"${change:+.2f}",
                "change_percent": f"{change_percent:+.2f}%",
                "previous_close": f"${float(quote_data.get('08. previous close', 0)):.2f}",
                "open": f"${float(quote_data.get('02. open', 0)):.2f}",
                "high": f"${float(quote_data.get('03. high', 0)):.2f}",
                "low": f"${float(quote_data.get('04. low', 0)):.2f}",
                "volume": quote_data.get("06. volume", "0"),
                "latest_trading_day": quote_data.get("07. latest trading day", ""),
                "is_positive": change >= 0
            }
        except (ValueError, KeyError) as e:
            raise Exception(f"Error parsing stock data for {symbol}: {e}")
