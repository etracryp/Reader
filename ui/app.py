import sys
import os
# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import asyncio
import threading
import time
from services.price_monitor import PriceMonitor
from services.arbitrage_engine import ArbitrageEngine
from services.safety_controller import SafetyController
from exchanges.websocket_manager import WebSocketManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Global state
exchange_status = {
    'cex': {'connected': False, 'last_update': None},
    'gate': {'connected': False, 'last_update': None},
    'binance': {'connected': False, 'last_update': None}
}

price_data = {}
arbitrage_opportunities = []

class TradingSystem:
    def __init__(self):
        self.price_monitor = PriceMonitor()
        self.arbitrage_engine = ArbitrageEngine()
        self.safety_controller = SafetyController()
        self.ws_manager = WebSocketManager()
        self.running = False
        
    async def start(self):
        self.running = True
        await self.price_monitor.start()
        
    def stop(self):
        self.running = False

trading_system = TradingSystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify({
        'exchanges': exchange_status,
        'price_data': price_data,
        'opportunities': arbitrage_opportunities
    })

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status_update', {
        'exchanges': exchange_status,
        'price_data': price_data,
        'opportunities': arbitrage_opportunities
    })

def update_exchange_status(exchange, connected, last_update=None):
    exchange_status[exchange]['connected'] = connected
    exchange_status[exchange]['last_update'] = last_update or time.time()
    socketio.emit('status_update', {
        'exchanges': exchange_status,
        'price_data': price_data,
        'opportunities': arbitrage_opportunities
    })

def price_callback(exchange, symbol, price_data_dict):
    """Handle price updates and emit to UI (synchronous wrapper)"""
    global price_data
    
    print(f"🔔 Price update received: {exchange} {symbol} {price_data_dict}")
    
    if symbol not in price_data:
        price_data[symbol] = {}
    
    # Extract the actual price value
    price_value = None
    if 'last' in price_data_dict:
        price_value = float(price_data_dict['last'])
    elif 'c' in price_data_dict:  # Binance format
        price_value = float(price_data_dict['c'])
    
    if price_value:
        # Extract bid and ask prices
        bid_price = float(price_data_dict.get('highest_bid', 0))
        ask_price = float(price_data_dict.get('lowest_ask', 0))
        
        price_data[symbol][exchange] = {
            'price': price_value,
            'last': price_value,
            'highest_bid': bid_price,
            'lowest_ask': ask_price,
            'exchange': exchange,
            'timestamp': time.time(),
            'raw_data': price_data_dict
        }
        
        # Update exchange status
        update_exchange_status(exchange, True)
        
        # Check for arbitrage opportunities
        try:
            trading_system.arbitrage_engine.update_price(exchange, symbol, price_value)
        except Exception as e:
            print(f"Error updating arbitrage engine: {e}")
        
        # Emit price update to UI with bid/ask data
        socketio.emit('price_update', {
            'exchange': exchange,
            'symbol': symbol,
            'data': {
                'price': price_value,
                'last': price_value,
                'highest_bid': bid_price,
                'lowest_ask': ask_price,
                'exchange': exchange,
                'timestamp': time.time()
            }
        })
        
        print(f"📊 Updated price for {symbol} on {exchange}: ${price_value}")

def arbitrage_callback(opportunity):
    """Handle arbitrage opportunities"""
    global arbitrage_opportunities
    arbitrage_opportunities.append(opportunity)
    
    # Keep only last 10 opportunities
    if len(arbitrage_opportunities) > 10:
        arbitrage_opportunities = arbitrage_opportunities[-10:]
    
    socketio.emit('opportunity_update', {
        'opportunities': arbitrage_opportunities
    })

def run_trading_system():
    """Run the trading system in background"""
    try:
        print("🚀 Starting trading system...")
        
        # Set up callbacks
        trading_system.price_monitor.register_callback(price_callback)
        trading_system.arbitrage_engine.set_opportunity_callback(arbitrage_callback)
        
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Start the trading system
        loop.run_until_complete(trading_system.start())
    except Exception as e:
        print(f"❌ Error in trading system: {e}")
        import traceback
        traceback.print_exc()

def start_trading_system():
    """Start trading system in a separate thread"""
    trading_thread = threading.Thread(target=run_trading_system)
    trading_thread.daemon = True
    trading_thread.start()

if __name__ == '__main__':
    print("🌐 Starting Web UI...")
    
    # Start trading system in background
    start_trading_system()
    
    # Start Flask app
    print("🚀 Web UI ready at http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 