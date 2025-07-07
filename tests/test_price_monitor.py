import pytest
import asyncio
from services.price_monitor import PriceMonitor

class DummyWSManager:
    def __init__(self):
        self.connected = False
        self.subscribed = False
        self.callback = None
    async def connect_all(self):
        self.connected = True
    async def subscribe_to_tickers(self, pairs):
        self.subscribed = True
    def register_price_callback(self, cb):
        self.callback = cb
    async def start_listening(self):
        # Simulate a price update
        if self.callback:
            await self.callback('binance', 'BTCUSDT', {'price': 60000})

@pytest.mark.asyncio
async def test_price_monitor_callback(monkeypatch):
    monitor = PriceMonitor()
    # Patch ws_manager with dummy
    monitor.ws_manager = DummyWSManager()
    results = []
    async def cb(exchange, symbol, price_data):
        results.append((exchange, symbol, price_data))
    monitor.register_callback(cb)
    await monitor.start()
    assert results and results[0][0] == 'binance' and results[0][1] == 'BTCUSDT' and results[0][2]['price'] == 60000 