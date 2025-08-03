# Placeholder for Price Monitor Service 

import asyncio
from exchanges.websocket_manager import WebSocketManager
from typing import Callable, Dict, Any

class PriceMonitor:
    def __init__(self, pairs=None):
        self.ws_manager = WebSocketManager()
        self.price_callback = None
        self.pairs = pairs or {
            'cex': ['BTCUSDT', 'ETHUSDT'],
            'gate': ['BTCUSDT', 'ETHUSDT'],
            'binance': ['BTCUSDT', 'ETHUSDT']
        }

    def register_callback(self, callback: Callable[[str, str, Dict[str, Any]], None]):
        """Register a callback for price updates"""
        self.price_callback = callback

    async def start(self):
        """Start the price monitoring system"""
        try:
            print("🔌 Connecting to exchanges...")
            await self.ws_manager.connect_all()
            
            print("📡 Subscribing to tickers...")
            await self.ws_manager.subscribe_to_tickers(self.pairs)
            
            print("👂 Registering price callback...")
            self.ws_manager.register_price_callback(self._on_price_update)
            
            print("🚀 Starting price monitoring...")
            await self.ws_manager.start_listening()
            
        except Exception as e:
            print(f"❌ Error starting price monitor: {e}")
            raise

    async def _on_price_update(self, exchange, symbol, price_data):
        """Handle price updates from exchanges"""
        try:
            if self.price_callback:
                # Call the callback (it's now synchronous)
                self.price_callback(exchange, symbol, price_data)
            else:
                print(f'Price update: {exchange} {symbol} {price_data}')
        except Exception as e:
            print(f"❌ Error in price callback: {e}")

# Example usage
async def print_price(exchange, symbol, price_data):
    print(f'[{exchange}] {symbol}: {price_data}')

async def main():
    monitor = PriceMonitor()
    monitor.register_callback(print_price)
    await monitor.start()

if __name__ == '__main__':
    asyncio.run(main()) 