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
        self.price_callback = callback

    async def start(self):
        await self.ws_manager.connect_all()
        await self.ws_manager.subscribe_to_tickers(self.pairs)
        self.ws_manager.register_price_callback(self._on_price_update)
        await self.ws_manager.start_listening()

    async def _on_price_update(self, exchange, symbol, price_data):
        if self.price_callback:
            await self.price_callback(exchange, symbol, price_data)
        else:
            print(f'Price update: {exchange} {symbol} {price_data}')

# Example usage
async def print_price(exchange, symbol, price_data):
    print(f'[{exchange}] {symbol}: {price_data}')

async def main():
    monitor = PriceMonitor()
    monitor.register_callback(print_price)
    await monitor.start()

if __name__ == '__main__':
    asyncio.run(main()) 