import pytest
import asyncio
from services.order_manager import OrderManager

@pytest.mark.asyncio
async def test_order_manager_success():
    manager = OrderManager()
    results = []
    manager.register_callback(lambda r: results.append(r))
    opportunity = {
        'symbol': 'BTCUSDT',
        'buy_exchange': 'binance',
        'sell_exchange': 'cex',
        'buy_price': 60000,
        'sell_price': 60200
    }
    await manager.submit_arbitrage_opportunity(opportunity, amount=0.01)
    assert results and results[0]['status'] == 'success'

@pytest.mark.asyncio
async def test_order_manager_buy_fail(monkeypatch):
    manager = OrderManager()
    results = []
    manager.register_callback(lambda r: results.append(r))
    async def fail_place_order(*a, **kw):
        return {'status': 'failed', 'reason': 'buy_failed'}
    manager.place_order = fail_place_order
    opportunity = {
        'symbol': 'BTCUSDT',
        'buy_exchange': 'binance',
        'sell_exchange': 'cex',
        'buy_price': 60000,
        'sell_price': 60200
    }
    await manager.submit_arbitrage_opportunity(opportunity, amount=0.01)
    assert results and results[0]['status'] == 'failed' and results[0]['reason'] == 'buy_failed'

@pytest.mark.asyncio
async def test_order_manager_sell_fail(monkeypatch):
    manager = OrderManager()
    results = []
    manager.register_callback(lambda r: results.append(r))
    # Patch place_order to simulate buy success, sell fail
    async def place_order(exchange, symbol, side, amount, price):
        if side == 'buy':
            return {'status': 'filled'}
        else:
            return {'status': 'failed', 'reason': 'sell_failed'}
    manager.place_order = place_order
    opportunity = {
        'symbol': 'BTCUSDT',
        'buy_exchange': 'binance',
        'sell_exchange': 'cex',
        'buy_price': 60000,
        'sell_price': 60200
    }
    await manager.submit_arbitrage_opportunity(opportunity, amount=0.01)
    assert results and results[0]['status'] == 'failed' and results[0]['reason'] == 'sell_failed' 