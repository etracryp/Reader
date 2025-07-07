import asyncio
import json
import hmac
import hashlib
import time
import websockets
from typing import Dict, List, Optional, Callable
import os
from dotenv import load_dotenv
import aiohttp

load_dotenv()

class BinanceWebSocket:
    def __init__(self):
        self.ws_url = 'wss://stream.binance.com:9443/ws/'
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.websocket = None
        self.is_connected = False
        self.callbacks = {}
        self.streams = []
        
    async def connect(self):
        """Establish WebSocket connection to Binance"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.is_connected = True
            print("Connected to Binance WebSocket")
            return True
        except Exception as e:
            print(f"Failed to connect to Binance: {e}")
            return False
    
    async def disconnect(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            print("Disconnected from Binance WebSocket")
    
    async def send_message(self, message: Dict):
        """Send message to Binance WebSocket"""
        if not self.is_connected:
            raise Exception("Not connected to Binance WebSocket")
        
        await self.websocket.send(json.dumps(message))
    
    async def subscribe_to_ticker(self, symbols: List[str]):
        """Subscribe to ticker data for specified symbols"""
        streams = [f"{symbol.lower()}@ticker" for symbol in symbols]
        self.streams.extend(streams)
        
        # Binance uses a single WebSocket connection with multiple streams
        combined_stream = "/".join(streams)
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": streams,
            "id": int(time.time() * 1000)
        }
        
        await self.send_message(subscribe_message)
        print(f"Subscribed to ticker streams: {streams}")
    
    async def subscribe_to_orderbook(self, symbols: List[str], depth: str = "5"):
        """Subscribe to orderbook data for specified symbols"""
        streams = [f"{symbol.lower()}@depth{depth}@100ms" for symbol in symbols]
        self.streams.extend(streams)
        
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": streams,
            "id": int(time.time() * 1000)
        }
        
        await self.send_message(subscribe_message)
        print(f"Subscribed to orderbook streams: {streams}")
    
    async def subscribe_to_trades(self, symbols: List[str]):
        """Subscribe to trade data for specified symbols"""
        streams = [f"{symbol.lower()}@trade" for symbol in symbols]
        self.streams.extend(streams)
        
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": streams,
            "id": int(time.time() * 1000)
        }
        
        await self.send_message(subscribe_message)
        print(f"Subscribed to trade streams: {streams}")
    
    async def subscribe_to_kline(self, symbols: List[str], interval: str = "1m"):
        """Subscribe to kline/candlestick data for specified symbols"""
        streams = [f"{symbol.lower()}@kline_{interval}" for symbol in symbols]
        self.streams.extend(streams)
        
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": streams,
            "id": int(time.time() * 1000)
        }
        
        await self.send_message(subscribe_message)
        print(f"Subscribed to kline streams: {streams}")
    
    async def subscribe_to_mini_ticker(self, symbols: List[str]):
        """Subscribe to mini ticker data for specified symbols"""
        streams = [f"{symbol.lower()}@miniTicker" for symbol in symbols]
        self.streams.extend(streams)
        
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": streams,
            "id": int(time.time() * 1000)
        }
        
        await self.send_message(subscribe_message)
        print(f"Subscribed to mini ticker streams: {streams}")
    
    async def subscribe_to_all_market_mini_tickers(self):
        """Subscribe to all market mini tickers"""
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": ["!miniTicker@arr"],
            "id": int(time.time() * 1000)
        }
        
        await self.send_message(subscribe_message)
        print("Subscribed to all market mini tickers")
    
    async def subscribe_to_all_market_tickers(self):
        """Subscribe to all market tickers"""
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": ["!ticker@arr"],
            "id": int(time.time() * 1000)
        }
        
        await self.send_message(subscribe_message)
        print("Subscribed to all market tickers")
    
    async def ping(self):
        """Send ping to keep connection alive"""
        ping_message = {
            "method": "ping",
            "id": int(time.time() * 1000)
        }
        await self.send_message(ping_message)
    
    def register_callback(self, event_type: str, callback: Callable):
        """Register callback for specific event types"""
        self.callbacks[event_type] = callback
    
    async def handle_message(self, message: str):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            
            # Handle different message types
            if 'stream' in data:
                stream = data['stream']
                stream_data = data['data']
                
                if '@ticker' in stream:
                    await self._handle_ticker(stream_data)
                elif '@depth' in stream:
                    await self._handle_orderbook(stream_data)
                elif '@trade' in stream:
                    await self._handle_trade(stream_data)
                elif '@kline_' in stream:
                    await self._handle_kline(stream_data)
                elif '@miniTicker' in stream:
                    await self._handle_mini_ticker(stream_data)
                else:
                    print(f"Unknown stream: {stream}")
            
            # Handle array responses (all market data)
            elif isinstance(data, list):
                if len(data) > 0 and 's' in data[0]:
                    if 'P' in data[0]:  # Mini ticker
                        await self._handle_all_mini_tickers(data)
                    else:  # Full ticker
                        await self._handle_all_tickers(data)
            
            # Handle ping/pong responses
            elif 'pong' in data:
                print("Received pong from Binance")
            
            # Handle subscription responses
            elif 'result' in data:
                print(f"Subscription result: {data}")
            
            # Call registered callback if exists
            if 'stream' in data and data['stream'] in self.callbacks:
                await self.callbacks[data['stream']](data)
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse Binance message: {e}")
        except Exception as e:
            print(f"Error handling Binance message: {e}")
    
    async def _handle_ticker(self, data: Dict):
        """Handle ticker data"""
        print(f"Binance Ticker: {data}")
    
    async def _handle_orderbook(self, data: Dict):
        """Handle orderbook data"""
        print(f"Binance Orderbook: {data}")
    
    async def _handle_trade(self, data: Dict):
        """Handle trade data"""
        print(f"Binance Trade: {data}")
    
    async def _handle_kline(self, data: Dict):
        """Handle kline/candlestick data"""
        print(f"Binance Kline: {data}")
    
    async def _handle_mini_ticker(self, data: Dict):
        """Handle mini ticker data"""
        print(f"Binance Mini Ticker: {data}")
    
    async def _handle_all_mini_tickers(self, data: List):
        """Handle all market mini tickers"""
        print(f"Binance All Mini Tickers: {len(data)} symbols")
    
    async def _handle_all_tickers(self, data: List):
        """Handle all market tickers"""
        print(f"Binance All Tickers: {len(data)} symbols")
    
    async def listen(self):
        """Main listening loop"""
        if not self.is_connected:
            await self.connect()
        
        try:
            while self.is_connected:
                message = await self.websocket.recv()
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("Binance WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            print(f"Error in Binance listen loop: {e}")
            self.is_connected = False

async def get_fees():
    """Fetch spot trading fees from Binance REST API (requires API key/secret in env)."""
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    if not api_key or not api_secret:
        return {'error': 'Missing Binance API key or secret'}
    url = 'https://api.binance.com/sapi/v1/asset/tradeFee'
    timestamp = int(time.time() * 1000)
    query = f'timestamp={timestamp}'
    signature = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    full_url = f'{url}?{query}&signature={signature}'
    headers = {'X-MBX-APIKEY': api_key}
    async with aiohttp.ClientSession() as session:
        async with session.get(full_url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                return {'error': f'HTTP {resp.status}'}

# Example usage
async def main():
    binance = BinanceWebSocket()
    await binance.connect()
    await binance.subscribe_to_ticker(['BTCUSDT', 'ETHUSDT'])
    await binance.subscribe_to_orderbook(['BTCUSDT'])
    await binance.listen()

if __name__ == "__main__":
    asyncio.run(main()) 