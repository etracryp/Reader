# Placeholder for Arbitrage Engine Service 

import asyncio
from utils.fees import get_all_fees

class ArbitrageEngine:
    def __init__(self, min_profit_threshold=0.001):
        self.price_data = {}  # {symbol: {exchange: price}}
        self.fees = {}        # {exchange: {symbol: {maker, taker}}}
        self.min_profit_threshold = min_profit_threshold
        self.opportunity_callback = None

    async def load_fees(self):
        self.fees = await get_all_fees()

    def update_price(self, exchange, symbol, price):
        if symbol not in self.price_data:
            self.price_data[symbol] = {}
        self.price_data[symbol][exchange] = price

    def set_opportunity_callback(self, callback):
        self.opportunity_callback = callback

    def calculate_profit(self, buy_price, sell_price, buy_fee, sell_fee):
        # Profit after fees (fees are in percent, e.g., 0.001 = 0.1%)
        cost = buy_price * (1 + buy_fee)
        revenue = sell_price * (1 - sell_fee)
        return revenue - cost

    def check_opportunities(self):
        # For each symbol, check all exchange pairs
        for symbol, prices in self.price_data.items():
            exchanges = list(prices.keys())
            for i in range(len(exchanges)):
                for j in range(len(exchanges)):
                    if i == j:
                        continue
                    buy_ex = exchanges[i]
                    sell_ex = exchanges[j]
                    buy_price = prices[buy_ex]
                    sell_price = prices[sell_ex]
                    # Get fees (default to 0.001 if unknown)
                    buy_fee = self._get_fee(buy_ex, symbol, 'taker')
                    sell_fee = self._get_fee(sell_ex, symbol, 'taker')
                    profit = self.calculate_profit(buy_price, sell_price, buy_fee, sell_fee)
                    profit_pct = profit / buy_price if buy_price else 0
                    if profit_pct >= self.min_profit_threshold:
                        opportunity = {
                            'symbol': symbol,
                            'buy_exchange': buy_ex,
                            'sell_exchange': sell_ex,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'buy_fee': buy_fee,
                            'sell_fee': sell_fee,
                            'profit': profit,
                            'profit_pct': profit_pct
                        }
                        if self.opportunity_callback:
                            self.opportunity_callback(opportunity)
                        else:
                            print('Arbitrage Opportunity:', opportunity)

    def _get_fee(self, exchange, symbol, fee_type):
        # Try to get the fee for the symbol, else default to 0.001 (0.1%)
        ex_fees = self.fees.get(exchange, {})
        if isinstance(ex_fees, dict):
            # Binance returns a list of dicts per symbol
            if exchange == 'binance' and isinstance(ex_fees, list):
                for entry in ex_fees:
                    if entry.get('symbol', '').upper() == symbol.upper():
                        return float(entry.get(fee_type + 'Commission', 0.001))
            # CEX/Gate: try symbol, else default
            symbol_fees = ex_fees.get(symbol) or ex_fees.get(symbol.replace('USDT', 'USD')) or {}
            return float(symbol_fees.get(fee_type, 0.001))
        return 0.001

# Example usage
async def main():
    engine = ArbitrageEngine(min_profit_threshold=0.002)
    await engine.load_fees()
    # Simulate price updates
    engine.update_price('binance', 'BTCUSDT', 60000)
    engine.update_price('cex', 'BTCUSDT', 60200)
    engine.update_price('gate', 'BTCUSDT', 60100)
    engine.check_opportunities()

if __name__ == '__main__':
    asyncio.run(main()) 