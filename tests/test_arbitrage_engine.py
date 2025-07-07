import pytest
import asyncio
from services.arbitrage_engine import ArbitrageEngine

@pytest.mark.asyncio
async def test_arbitrage_opportunity_detection():
    engine = ArbitrageEngine(min_profit_threshold=0.001)
    await engine.load_fees()
    # Use dummy fees for deterministic test
    engine.fees = {
        'binance': {'BTCUSDT': {'taker': 0.001}},
        'cex': {'BTCUSDT': {'taker': 0.001}},
        'gate': {'BTCUSDT': {'taker': 0.001}}
    }
    # Simulate price updates
    engine.update_price('binance', 'BTCUSDT', 60000)
    engine.update_price('cex', 'BTCUSDT', 60200)
    engine.update_price('gate', 'BTCUSDT', 60100)
    found = []
    def cb(op):
        found.append(op)
    engine.set_opportunity_callback(cb)
    engine.check_opportunities()
    assert any(
        op['buy_exchange'] == 'binance' and op['sell_exchange'] == 'cex' for op in found
    )
    # Test no opportunity if profit below threshold
    engine = ArbitrageEngine(min_profit_threshold=0.1)
    engine.fees = {
        'binance': {'BTCUSDT': {'taker': 0.001}},
        'cex': {'BTCUSDT': {'taker': 0.001}}
    }
    engine.update_price('binance', 'BTCUSDT', 60000)
    engine.update_price('cex', 'BTCUSDT', 60100)
    found = []
    engine.set_opportunity_callback(lambda op: found.append(op))
    engine.check_opportunities()
    assert not found 