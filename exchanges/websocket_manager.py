import asyncio
import json
import time
from typing import Dict, List, Optional, Callable
from .cex import CEXIOWebSocket
from .gate import GateIOWebSocket
from .binance import BinanceWebSocket

class WebSocketManager:
    def __init__(self):
        self.cex = CEXIOWebSocket()
        self.gate = GateIOWebSocket()
        self.binance = BinanceWebSocket()
        self.exchanges = {
            'cex': self.cex,
            'gate': self.gate,
            'binance': self.binance
        }
        self.price_data = {}
        self.callbacks = {}
        
    async def connect_all(self):
        """Connect to all exchanges"""
        tasks = []
        for name, exchange in self.exchanges.items():
            task = asyncio.create_task(self._connect_exchange(name, exchange))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for name, result in zip(self.exchanges.keys(), results):
            if isinstance(result, Exception):
                print(f"Failed to connect to {name}: {result}")
            else:
                print(f"Successfully connected to {name}")
    
    async def _connect_exchange(self, name: str, exchange):
        """Connect to a specific exchange"""
        try:
            await exchange.connect()
            if name == 'cex':
                await exchange.authenticate()
            elif name == 'gate':
                await exchange.authenticate()
            return True
        except Exception as e:
            print(f"Error connecting to {name}: {e}")
            return False
    
    async def subscribe_to_tickers(self, pairs: Dict[str, List[str]]):
        """Subscribe to ticker data for all exchanges"""
        tasks = []
        
        # CEX.IO pairs (format: BTC:USD)
        if 'cex' in pairs:
            cex_pairs = [pair.replace('USDT', 'USD') for pair in pairs['cex']]
            tasks.append(self.cex.subscribe_to_ticker(cex_pairs))
        
        # Gate.io pairs (format: BTC_USDT)
        if 'gate' in pairs:
            gate_pairs = [pair.replace('USDT', '_USDT') for pair in pairs['gate']]
            tasks.append(self.gate.subscribe_to_ticker(gate_pairs))
        
        # Binance pairs (format: BTCUSDT)
        if 'binance' in pairs:
            tasks.append(self.binance.subscribe_to_ticker(pairs['binance']))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def subscribe_to_orderbooks(self, pairs: Dict[str, List[str]]):
        """Subscribe to orderbook data for all exchanges"""
        tasks = []
        
        if 'cex' in pairs:
            cex_pairs = [pair.replace('USDT', 'USD') for pair in pairs['cex']]
            tasks.append(self.cex.subscribe_to_orderbook(cex_pairs))
        
        if 'gate' in pairs:
            gate_pairs = [pair.replace('USDT', '_USDT') for pair in pairs['gate']]
            tasks.append(self.gate.subscribe_to_orderbook(gate_pairs))
        
        if 'binance' in pairs:
            tasks.append(self.binance.subscribe_to_orderbook(pairs['binance']))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def subscribe_to_trades(self, pairs: Dict[str, List[str]]):
        """Subscribe to trade data for all exchanges"""
        tasks = []
        
        if 'cex' in pairs:
            cex_pairs = [pair.replace('USDT', 'USD') for pair in pairs['cex']]
            tasks.append(self.cex.subscribe_to_trades(cex_pairs))
        
        if 'gate' in pairs:
            gate_pairs = [pair.replace('USDT', '_USDT') for pair in pairs['gate']]
            tasks.append(self.gate.subscribe_to_trades(gate_pairs))
        
        if 'binance' in pairs:
            tasks.append(self.binance.subscribe_to_trades(pairs['binance']))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def register_price_callback(self, callback: Callable):
        """Register callback for price updates"""
        self.price_callback = callback
    
    async def handle_price_update(self, exchange: str, symbol: str, price_data: Dict):
        """Handle price updates from any exchange"""
        if not hasattr(self, 'price_callback'):
            return
        
        # Normalize symbol format
        normalized_symbol = symbol.replace('_', '').replace(':', '')
        
        if normalized_symbol not in self.price_data:
            self.price_data[normalized_symbol] = {}
        
        self.price_data[normalized_symbol][exchange] = price_data
        
        # Call the registered callback
        await self.price_callback(exchange, normalized_symbol, price_data)
    
    async def start_listening(self):
        """Start listening to all exchanges"""
        tasks = []
        
        # Set up message handlers for each exchange
        for name, exchange in self.exchanges.items():
            if name == 'cex':
                exchange.register_callback('tick', lambda data: self._handle_cex_tick(data))
            elif name == 'gate':
                exchange.register_callback('spot.tickers', lambda data: self._handle_gate_tick(data))
            elif name == 'binance':
                exchange.register_callback('ticker', lambda data: self._handle_binance_tick(data))
            
            # Start listening
            task = asyncio.create_task(exchange.listen())
            tasks.append(task)
        
        # Wait for all listening tasks
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _handle_cex_tick(self, data: Dict):
        """Handle CEX.IO ticker data"""
        if 'data' in data and 'pair' in data['data']:
            symbol = data['data']['pair']
            await self.handle_price_update('cex', symbol, data['data'])
    
    async def _handle_gate_tick(self, data: Dict):
        """Handle Gate.io ticker data"""
        if 'result' in data and 'currency_pair' in data['result']:
            symbol = data['result']['currency_pair']
            await self.handle_price_update('gate', symbol, data['result'])
    
    async def _handle_binance_tick(self, data: Dict):
        """Handle Binance ticker data"""
        if 's' in data:  # Symbol
            symbol = data['s']
            await self.handle_price_update('binance', symbol, data)
    
    async def disconnect_all(self):
        """Disconnect from all exchanges"""
        tasks = []
        for exchange in self.exchanges.values():
            task = asyncio.create_task(exchange.disconnect())
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_price_data(self, symbol: str) -> Dict:
        """Get current price data for a symbol across all exchanges"""
        return self.price_data.get(symbol, {})
    
    def get_arbitrage_opportunities(self, symbol: str, min_profit_threshold: float = 0.001):
        """Find arbitrage opportunities for a symbol"""
        prices = self.price_data.get(symbol, {})
        if len(prices) < 2:
            return []
        
        opportunities = []
        exchanges = list(prices.keys())
        
        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                ex1, ex2 = exchanges[i], exchanges[j]
                
                # Extract bid/ask prices (simplified - you'll need to adapt based on actual data structure)
                price1 = self._extract_price(prices[ex1])
                price2 = self._extract_price(prices[ex2])
                
                if price1 and price2:
                    profit_pct = abs(price1 - price2) / min(price1, price2)
                    
                    if profit_pct > min_profit_threshold:
                        opportunities.append({
                            'symbol': symbol,
                            'buy_exchange': ex1 if price1 < price2 else ex2,
                            'sell_exchange': ex2 if price1 < price2 else ex1,
                            'buy_price': min(price1, price2),
                            'sell_price': max(price1, price2),
                            'profit_pct': profit_pct
                        })
        
        return opportunities
    
    def _extract_price(self, price_data: Dict) -> Optional[float]:
        """Extract price from exchange-specific data structure"""
        # This is a simplified version - you'll need to adapt based on actual data
        if 'last' in price_data:
            return float(price_data['last'])
        elif 'c' in price_data:  # Binance close price
            return float(price_data['c'])
        return None

# Example usage
async def price_callback(exchange: str, symbol: str, price_data: Dict):
    """Example callback for price updates"""
    print(f"Price update - {exchange}: {symbol} = {price_data}")

async def main():
    manager = WebSocketManager()
    await manager.connect_all()
    
    # Subscribe to common pairs
    pairs = {
        'cex': ['BTCUSDT', 'ETHUSDT'],
        'gate': ['BTCUSDT', 'ETHUSDT'],
        'binance': ['BTCUSDT', 'ETHUSDT']
    }
    
    await manager.subscribe_to_tickers(pairs)
    manager.register_price_callback(price_callback)
    
    # Start listening
    await manager.start_listening()

if __name__ == "__main__":
    asyncio.run(main()) 