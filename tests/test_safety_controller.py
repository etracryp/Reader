import time
import pytest
from services.safety_controller import SafetyController

def test_can_trade_limits():
    safety = SafetyController(max_daily_trades=2, max_position_size=100, trade_cooldown=1, min_balance=10)
    # Should be able to trade
    allowed, reason = safety.can_trade('BTCUSDT', 50, balance=100)
    assert allowed and reason == 'ok'
    # Exceed position size
    allowed, reason = safety.can_trade('BTCUSDT', 200, balance=300)
    assert not allowed and reason == 'max_position_size'
    # Insufficient balance
    allowed, reason = safety.can_trade('BTCUSDT', 50, balance=40)
    assert not allowed and reason == 'insufficient_balance'
    # Record a trade and test cooldown
    safety.record_trade('BTCUSDT', 50)
    allowed, reason = safety.can_trade('BTCUSDT', 50, balance=100)
    assert not allowed and reason == 'trade_cooldown'
    # Wait for cooldown
    time.sleep(1.1)
    allowed, reason = safety.can_trade('BTCUSDT', 50, balance=100)
    assert allowed
    # Hit daily trade limit
    safety.record_trade('BTCUSDT', 50)
    allowed, reason = safety.can_trade('BTCUSDT', 50, balance=100)
    assert not allowed and reason == 'daily_trade_limit'

def test_emergency_stop_and_resume():
    safety = SafetyController()
    safety.emergency_stop()
    allowed, reason = safety.can_trade('BTCUSDT', 10, balance=100)
    assert not allowed and reason == 'emergency_stop'
    safety.resume()
    allowed, reason = safety.can_trade('BTCUSDT', 10, balance=100)
    assert allowed

def test_reset_daily_limits():
    safety = SafetyController(max_daily_trades=1, trade_cooldown=1)
    safety.record_trade('BTCUSDT', 10)
    allowed, reason = safety.can_trade('BTCUSDT', 10, balance=100)
    assert not allowed and reason == 'daily_trade_limit'
    safety.reset_daily_limits()
    time.sleep(1.1)  # Wait for cooldown to expire
    allowed, reason = safety.can_trade('BTCUSDT', 10, balance=100)
    assert allowed

def test_trade_log():
    safety = SafetyController()
    assert safety.trade_log == []
    safety.record_trade('BTCUSDT', 5)
    assert len(safety.trade_log) == 1
    t, sym, amt = safety.trade_log[0]
    assert sym == 'BTCUSDT' and amt == 5 