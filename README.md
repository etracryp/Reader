# Multi-Exchange Arbitrage Trading System

## Overview

This arbitrage trading system monitors price differences across multiple cryptocurrency exchanges (CEX.IO, Gate.io, and Binance) to identify and execute profitable arbitrage opportunities in real-time. The system uses WebSocket connections for low-latency price monitoring and includes sophisticated safeguards to prevent overuse and ensure safe trading operations.

## Features

- **Multi-Exchange Support**: CEX.IO, Gate.io, and Binance integration
- **Real-time Price Monitoring**: WebSocket-based price feeds for minimal latency
- **Arbitrage Detection**: Automated scanning for profitable opportunities
- **Fee Calculation**: Automatic transaction fee deduction for accurate profit calculation
- **Safety Mechanisms**: Built-in safeguards to prevent system overuse
- **Order Confirmation**: Waits for sell confirmation before executing new buy orders
- **Risk Management**: Configurable limits and thresholds
- **Web UI**: Real-time monitoring interface with exchange status and price comparison

## Quick Start

### 1. Automatic Environment Setup

The easiest way to get started is to use the automatic environment setup script:

```bash
# Run the environment setup script
python scripts/setup_env.py
```

This will create a complete `.env` file with all required environment variables. You'll just need to:

1. **Edit the `.env` file** and replace the placeholder values with your actual API keys
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Start the system**: `python main.py`
4. **Start the web UI**: `python ui/app.py`

### 2. Manual Setup (Alternative)

If you prefer to set up manually:

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file manually
cp .env.example .env  # (if .env.example exists)
# Then edit .env with your API keys
```

## Web UI

The system includes a web-based user interface for real-time monitoring:

### Features
- **Exchange Status Monitoring**: Real-time connection status for all exchanges
- **Price Comparison**: Side-by-side price display with BUY/SELL indicators
- **Arbitrage Opportunities**: Live detection and display of profitable opportunities
- **Profit Calculation**: Automatic profit percentage calculation

### How to Run the UI

1. **Install UI Dependencies**:
   ```bash
   pip install flask flask-socketio
   ```

2. **Start the Web Interface**:
   ```bash
   python ui/app.py
   ```

3. **Access the UI**:
   Open your browser and navigate to `http://localhost:5000`

### UI Components

#### Exchange Status Cards
- **Green Indicator**: Exchange is connected and receiving data
- **Red Indicator**: Exchange is disconnected or not responding
- **Last Update Time**: Shows when the exchange last sent price data

#### Price Comparison Grid
- **Symbol Cards**: Each trading pair gets its own card
- **Buy Price (Green)**: Lowest price across all exchanges (best to buy)
- **Sell Price (Red)**: Highest price across all exchanges (best to sell)
- **Potential Profit**: Calculated profit percentage if you buy low and sell high

#### Arbitrage Opportunities
- **High Profit (Green)**: Opportunities with >1% profit
- **Medium Profit (Orange)**: Opportunities with 0.5-1% profit
- **Low Profit (Red)**: Opportunities with <0.5% profit

### UI Instructions

1. **Monitor Exchange Status**: Check the status cards to ensure all exchanges are connected (green indicators)

2. **Analyze Price Differences**: 
   - Look for symbols with large price differences between exchanges
   - Green prices indicate the best buying opportunities
   - Red prices indicate the best selling opportunities

3. **Track Arbitrage Opportunities**:
   - The system automatically detects and displays profitable opportunities
   - Opportunities are color-coded by profit potential
   - Each opportunity shows the buy/sell exchanges and expected profit

4. **Real-time Updates**:
   - All data updates automatically via WebSocket
   - No need to refresh the page
   - Last update time is shown at the bottom

## Environment Variables

The system uses a comprehensive set of environment variables. The setup script creates a complete `.env` file with all required variables:

### Exchange API Credentials
```bash
# CEX.IO
CEXIO_API_KEY=your_cexio_api_key_here
CEXIO_API_SECRET=your_cexio_api_secret_here

# Gate.io
GATEIO_API_KEY=your_gateio_api_key_here
GATEIO_API_SECRET=your_gateio_api_secret_here

# Binance
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here
```

### Safety Settings
```bash
MIN_PROFIT_THRESHOLD=0.005  # 0.5%
MAX_DAILY_TRADES=50
MAX_POSITION_SIZE=1000      # USDT
TRADE_COOLDOWN=30           # seconds
```

### Web UI Settings
```bash
FLASK_SECRET_KEY=your-secret-key-change-this-in-production
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### Trading Configuration
```bash
MIN_TRADE_SIZE=10
RECONNECT_DELAY=5000
MAX_RECONNECT_ATTEMPTS=10
ORDER_TIMEOUT=30
```

### Advanced Settings
```bash
# Enable/disable specific exchanges
ENABLE_CEX=True
ENABLE_GATE=True
ENABLE_BINANCE=True

# Trading pairs to monitor
TRADING_PAIRS=BTCUSDT,ETHUSDT,BNBUSDT,ADAUSDT,DOTUSDT,LINKUSDT,LTCUSDT,BCHUSDT

# Development settings
DEBUG_MODE=True
TEST_MODE=False
```

## Supported Exchanges

### 1. CEX.IO
**API Documentation:**
- **REST API**: https://cex.io/rest-api
- **WebSocket API**: https://cex.io/websocket-api
- **Exchange V2 Documentation**: https://docs.cex.io/
- **Spot Trading Documentation**: https://trade.cex.io/docs/

**Key Features:**
- REST and WebSocket APIs available
- Supports Market and Limit orders
- Rate limit: 600 requests per 10 minutes for WebSocket
- Authentication: API key + HMAC-SHA256 signature

### 2. Gate.io
**API Documentation:**
- **API v4 Main Documentation**: https://www.gate.com/docs/developers/apiv4/en/
- **WebSocket API v4**: https://www.gate.com/docs/developers/apiv4/ws/en/
- **Futures API**: https://www.gate.com/docs/futures/api/index.html
- **Futures WebSocket**: https://www.gate.com/docs/developers/futures/ws/en/

**Key Features:**
- APIv4 supports spot, margin, and futures trading
- WebSocket endpoint: `wss://api.gateio.ws/ws/v4/`
- Comprehensive SDK support in multiple languages
- Rate limiting and IP-based restrictions

### 3. Binance
**API Documentation:**
- **Spot API Documentation**: https://developers.binance.com/docs/binance-spot-api-docs/rest-api
- **WebSocket API**: https://developers.binance.com/docs/binance-spot-api-docs/web-socket-api
- **WebSocket Streams**: https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams
- **User Data Streams**: https://developers.binance.com/docs/binance-spot-api-docs/user-data-stream

**Key Features:**
- Most liquid cryptocurrency exchange
- WebSocket endpoint: `wss://stream.binance.com:9443/ws/`
- Market data endpoint: `wss://data-stream.binance.vision`
- Advanced order types and features
- Rate limiting based on request weights

## System Architecture

### Core Components

1. **Price Monitor Service**
   - WebSocket connections to all exchanges
   - Real-time price data aggregation
   - Price difference calculation

2. **Arbitrage Engine**
   - Opportunity detection algorithm
   - Fee calculation and profit estimation
   - Risk assessment

3. **Order Management System**
   - Multi-exchange order execution
   - Order status tracking
   - Confirmation waiting mechanism

4. **Safety Controller**
   - Usage limits enforcement
   - Trading frequency controls
   - Emergency stop mechanisms

5. **Web UI**
   - Real-time status monitoring
   - Price comparison interface
   - Arbitrage opportunity display

### WebSocket Endpoints

```python
# Exchange WebSocket Endpoints
ENDPOINTS = {
    'cex': 'wss://ws.cex.io/ws/',
    'gate': 'wss://api.gateio.ws/ws/v4/',
    'binance': 'wss://stream.binance.com:9443/ws/'
}
```

### Key Trading Pairs
- BTC/USDT
- ETH/USDT
- BNB/USDT
- ADA/USDT
- DOT/USDT
- And more configurable pairs

## Safety Mechanisms

### 1. Order Confirmation System
- **Buy Protection**: System waits for sell order confirmation before placing new buy orders
- **Status Tracking**: Monitors order status across all exchanges
- **Timeout Handling**: Automatic order cancellation if not filled within timeout

### 2. Usage Limits
- **Daily Trade Limits**: Maximum number of trades per day
- **Volume Limits**: Maximum trading volume per time period
- **Frequency Controls**: Minimum time between trades
- **Balance Checks**: Ensures sufficient balance before trading

### 3. Risk Management
- **Minimum Profit Threshold**: Only execute trades above minimum profit margin
- **Maximum Position Size**: Limit exposure per trading pair
- **Stop Loss Mechanisms**: Automatic position closure on adverse movements
- **Emergency Stop**: Manual and automatic system shutdown

### 4. Fee Management
```python
# Fee Structure (example - update with actual fees)
EXCHANGE_FEES = {
    'cex': {
        'maker': 0.0025,  # 0.25%
        'taker': 0.0025   # 0.25%
    },
    'gate': {
        'maker': 0.002,   # 0.2%
        'taker': 0.002    # 0.2%
    },
    'binance': {
        'maker': 0.001,   # 0.1%
        'taker': 0.001    # 0.1%
    }
}
```

## Installation

### Prerequisites
- Python 3.10 or newer
- API keys for all three exchanges
- Sufficient balance on all exchanges

### Quick Installation
```bash
# 1. Clone the repository
git clone <repository-url>
cd Reader

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment (creates .env file)
python scripts/setup_env.py

# 5. Edit .env file with your API keys
# Edit the .env file and replace placeholder values

# 6. Start the system
python main.py

# 7. Start the web UI (in another terminal)
python ui/app.py
```

### Dependencies
```bash
pip install websockets
pip install aiohttp
pip install python-dotenv
pip install asyncio
pip install json
pip install hashlib
pip install hmac
pip install time
pip install flask
pip install flask-socketio
```

## Configuration

### Trading Parameters
```python
CONFIG = {
    # Minimum profit after fees (percentage)
    'min_profit_threshold': 0.5,
    
    # Maximum trade size in USDT
    'max_trade_size': 1000,
    
    # Minimum trade size in USDT
    'min_trade_size': 10,
    
    # Cooldown between trades (seconds)
    'trade_cooldown': 30,
    
    # WebSocket reconnection settings
    'reconnect_delay': 5000,
    'max_reconnect_attempts': 10,
    
    # Order timeout (seconds)
    'order_timeout': 30
}
```

### Monitored Trading Pairs
```python
TRADING_PAIRS = [
    'BTCUSDT',
    'ETHUSDT',
    'BNBUSDT',
    'ADAUSDT',
    'DOTUSDT',
    'LINKUSDT',
    'LTCUSDT',
    'BCHUSDT'
]
```

## Usage

### Basic Operation
1. Configure API keys for all exchanges
2. Set trading parameters and safety limits
3. Start the arbitrage monitoring system
4. Monitor logs and trading activities
5. Regularly review performance and adjust parameters

### Web UI Operation
1. Start the web interface: `python ui/app.py`
2. Open browser to `http://localhost:5000`
3. Monitor exchange status and price differences
4. Watch for arbitrage opportunities in real-time

### Monitoring and Logging
- Real-time price differences
- Executed trades and profits
- System health and connection status
- Error logs and warnings
- Daily/weekly performance reports

## Risk Considerations

⚠️ **Important Warnings:**

1. **Market Risk**: Cryptocurrency prices are highly volatile
2. **Liquidity Risk**: Order books may change rapidly
3. **Technical Risk**: API failures or network issues
4. **Regulatory Risk**: Different jurisdictions have different rules
5. **Fee Impact**: Transaction fees can eliminate small arbitrage opportunities

## Legal and Compliance

- Ensure compliance with local regulations
- Consider tax implications of frequent trading
- Review exchange terms of service
- Implement proper KYC/AML procedures
- Keep detailed records for audit purposes

## Performance Monitoring

### Key Metrics
- **Profit/Loss**: Track cumulative P&L
- **Success Rate**: Percentage of successful arbitrage trades
- **Average Profit**: Mean profit per successful trade
- **Execution Time**: Time from detection to execution
- **Slippage**: Difference between expected and actual prices

### Alerts and Notifications
- System errors and connection issues
- Large profit opportunities
- Safety limit breaches
- Daily performance summaries

## Troubleshooting

### Common Issues
1. **WebSocket Connection Drops**: Implement automatic reconnection
2. **API Rate Limits**: Respect exchange limits and implement backoff
3. **Order Execution Failures**: Handle partial fills and cancellations
4. **Price Feed Delays**: Monitor latency and switch feeds if needed

### Emergency Procedures
1. **Manual Stop**: Immediate system shutdown capability
2. **Position Closure**: Automatic closure of open positions
3. **Fund Recovery**: Manual withdrawal procedures
4. **Error Recovery**: System restart and state restoration

## Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request
5. Follow code review process

## License

[Specify your license here]

## Disclaimer

This software is for educational and informational purposes only. Cryptocurrency trading involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results. Use at your own risk.

## Support

For technical support or questions:
- Create an issue in the repository
- Review API documentation for each exchange
- Check system logs for error details
- Ensure all dependencies are up to date

---

**Last Updated**: July 2025  
**Version**: 1.0.0
