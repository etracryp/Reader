import pytest
import asyncio
import os
import websockets
from exchanges.cex import CEXIOWebSocket
from exchanges.gate import GateIOWebSocket
from exchanges.binance import BinanceWebSocket

pytestmark = pytest.mark.asyncio

async def test_cex_ws_connect_and_subscribe():
    cex = CEXIOWebSocket()
    connected = await cex.connect()
    assert connected, 'CEX.IO WebSocket failed to connect'
    # No authentication required for public ticker
    await cex.subscribe_to_ticker(['BTC:USD'])
    await asyncio.sleep(2)
    await cex.disconnect()

async def test_gate_ws_connect_and_subscribe():
    gate = GateIOWebSocket()
    connected = await gate.connect()
    assert connected, 'Gate.io WebSocket failed to connect'
    # No authentication required for public ticker
    await gate.subscribe_to_ticker(['BTC_USDT'])
    await asyncio.sleep(2)
    await gate.disconnect()

async def test_binance_ws_connect_and_subscribe():
    # Connect directly to a valid Binance ticker stream for BTCUSDT
    ws_url = 'wss://stream.binance.com:9443/ws/btcusdt@ticker'
    try:
        async with websockets.connect(ws_url) as ws:
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            assert msg, 'No message received from Binance ticker stream'
    except Exception as e:
        pytest.fail(f'Binance WebSocket test failed: {e}') 