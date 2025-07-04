import asyncio
import json
import hmac
import hashlib
import time
import websockets
from typing import Dict, List, Optional, Callable
import os
from dotenv import load_dotenv

load_dotenv()

class GateIOWebSocket:
    def __init__(self):
        self.ws_url = 'wss://api.gateio.ws/ws/v4/'
        self.api_key = os.getenv('GATEIO_API_KEY')
        self.api_secret = os.getenv('GATEIO_API_SECRET')
        self.websocket = None
        self.is_connected = False
        self.callbacks = {}
        self.channel_id = 0
        
    async def connect(self):
        """Establish WebSocket connection to Gate.io"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.is_connected = True
            print("Connected to Gate.io WebSocket")
            return True
        except Exception as e:
            print(f"Failed to connect to Gate.io: {e}")
            return False
    
    async def disconnect(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            print("Disconnected from Gate.io WebSocket")
    
    async def send_message(self, message: Dict):
        """Send message to Gate.io WebSocket"""
        if not self.is_connected:
            raise Exception("Not connected to Gate.io WebSocket")
        
        await self.websocket.send(json.dumps(message))
    
    def _get_channel_id(self) -> int:
        """Get unique channel ID for subscriptions"""
        self.channel_id += 1
        return self.channel_id
    
    async def authenticate(self):
        """Authenticate with Gate.io using API credentials"""
        if not self.api_key or not self.api_secret:
            print("Warning: Gate.io API credentials not found")
            return False
        
        timestamp = int(time.time())
        message = f"GET\n/realtime\n\n{timestamp}"
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        auth_message = {
            "time": timestamp,
            "channel": "spot.ping",
            "event": "subscribe",
            "auth": {
                "method": "api_key",
                "KEY": self.api_key,
                "SIGN": signature
            }
        }
        
        await self.send_message(auth_message)
        print("Authentication sent to Gate.io")
        return True
    
    async def subscribe_to_ticker(self, pairs: List[str]):
        """Subscribe to ticker data for specified pairs"""
        for pair in pairs:
            subscribe_message = {
                "time": int(time.time()),
                "channel": "spot.tickers",
                "event": "subscribe",
                "payload": [pair]
            }
            await self.send_message(subscribe_message)
            print(f"Subscribed to {pair} ticker on Gate.io")
    
    async def subscribe_to_orderbook(self, pairs: List[str], level: int = 5):
        """Subscribe to orderbook data for specified pairs"""
        for pair in pairs:
            subscribe_message = {
                "time": int(time.time()),
                "channel": "spot.order_book",
                "event": "subscribe",
                "payload": [pair, str(level), "100ms"]
            }
            await self.send_message(subscribe_message)
            print(f"Subscribed to {pair} orderbook on Gate.io")
    
    async def subscribe_to_trades(self, pairs: List[str]):
        """Subscribe to trade data for specified pairs"""
        for pair in pairs:
            subscribe_message = {
                "time": int(time.time()),
                "channel": "spot.trades",
                "event": "subscribe",
                "payload": [pair]
            }
            await self.send_message(subscribe_message)
            print(f"Subscribed to {pair} trades on Gate.io")
    
    async def subscribe_to_candlesticks(self, pairs: List[str], interval: str = "1m"):
        """Subscribe to candlestick data for specified pairs"""
        for pair in pairs:
            subscribe_message = {
                "time": int(time.time()),
                "channel": "spot.candlesticks",
                "event": "subscribe",
                "payload": [interval, pair]
            }
            await self.send_message(subscribe_message)
            print(f"Subscribed to {pair} candlesticks on Gate.io")
    
    async def ping(self):
        """Send ping to keep connection alive"""
        ping_message = {
            "time": int(time.time()),
            "channel": "spot.ping",
            "event": "subscribe",
            "payload": []
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
            if 'channel' in data:
                channel = data['channel']
                
                if channel == 'spot.tickers':
                    await self._handle_ticker(data)
                elif channel == 'spot.order_book':
                    await self._handle_orderbook(data)
                elif channel == 'spot.trades':
                    await self._handle_trade(data)
                elif channel == 'spot.candlesticks':
                    await self._handle_candlestick(data)
                elif channel == 'spot.ping':
                    await self._handle_ping(data)
                else:
                    print(f"Unknown channel: {channel}")
            
            # Call registered callback if exists
            if channel in self.callbacks:
                await self.callbacks[channel](data)
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse Gate.io message: {e}")
        except Exception as e:
            print(f"Error handling Gate.io message: {e}")
    
    async def _handle_ticker(self, data: Dict):
        """Handle ticker data"""
        print(f"Gate.io Ticker: {data}")
    
    async def _handle_orderbook(self, data: Dict):
        """Handle orderbook data"""
        print(f"Gate.io Orderbook: {data}")
    
    async def _handle_trade(self, data: Dict):
        """Handle trade data"""
        print(f"Gate.io Trade: {data}")
    
    async def _handle_candlestick(self, data: Dict):
        """Handle candlestick data"""
        print(f"Gate.io Candlestick: {data}")
    
    async def _handle_ping(self, data: Dict):
        """Handle ping response"""
        print("Received ping response from Gate.io")
    
    async def listen(self):
        """Main listening loop"""
        if not self.is_connected:
            await self.connect()
        
        try:
            while self.is_connected:
                message = await self.websocket.recv()
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("Gate.io WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            print(f"Error in Gate.io listen loop: {e}")
            self.is_connected = False

# Example usage
async def main():
    gate = GateIOWebSocket()
    await gate.connect()
    await gate.authenticate()
    await gate.subscribe_to_ticker(['BTC_USDT', 'ETH_USDT'])
    await gate.listen()

if __name__ == "__main__":
    asyncio.run(main()) 