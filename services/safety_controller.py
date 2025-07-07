# Placeholder for Safety Controller Service 
import time
from typing import Dict

class SafetyController:
    def __init__(self, max_daily_trades=50, max_position_size=1000, trade_cooldown=30, min_balance=0):
        self.max_daily_trades = max_daily_trades
        self.max_position_size = max_position_size  # per trade
        self.trade_cooldown = trade_cooldown  # seconds
        self.min_balance = min_balance
        self.daily_trade_count = 0
        self.daily_volume = 0.0
        self.last_trade_time = 0
        self.emergency_stopped = False
        self.trade_log = []  # List of (timestamp, symbol, amount)

    def can_trade(self, symbol: str, amount: float, balance: float = None) -> (bool, str):
        now = time.time()
        if self.emergency_stopped:
            return False, 'emergency_stop'
        if self.daily_trade_count >= self.max_daily_trades:
            return False, 'daily_trade_limit'
        if amount > self.max_position_size:
            return False, 'max_position_size'
        if now - self.last_trade_time < self.trade_cooldown:
            return False, 'trade_cooldown'
        if balance is not None and balance < amount + self.min_balance:
            return False, 'insufficient_balance'
        return True, 'ok'

    def record_trade(self, symbol: str, amount: float):
        self.daily_trade_count += 1
        self.daily_volume += amount
        self.last_trade_time = time.time()
        self.trade_log.append((self.last_trade_time, symbol, amount))

    def emergency_stop(self):
        self.emergency_stopped = True
        print('EMERGENCY STOP ACTIVATED!')

    def resume(self):
        self.emergency_stopped = False
        print('SafetyController: Trading resumed.')

    def reset_daily_limits(self):
        self.daily_trade_count = 0
        self.daily_volume = 0.0
        self.trade_log.clear()
        print('SafetyController: Daily limits reset.')

# Example usage
def main():
    safety = SafetyController(max_daily_trades=2, max_position_size=100, trade_cooldown=5)
    print(safety.can_trade('BTCUSDT', 10))
    safety.record_trade('BTCUSDT', 10)
    print(safety.can_trade('BTCUSDT', 10))
    safety.record_trade('BTCUSDT', 10)
    print(safety.can_trade('BTCUSDT', 10))  # Should hit daily limit
    safety.emergency_stop()
    print(safety.can_trade('BTCUSDT', 10))  # Should be stopped
    safety.resume()
    safety.reset_daily_limits()
    print(safety.can_trade('BTCUSDT', 10))

if __name__ == '__main__':
    main() 