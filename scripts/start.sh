#!/bin/bash

# Arbitrage Trading System Startup Script
echo "🚀 Starting Arbitrage Trading System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.10 or newer."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists, create if not
if [ ! -f ".env" ]; then
    echo "⚙️ Setting up environment variables..."
    python scripts/setup_env.py
    echo "⚠️  Please edit the .env file with your API keys before continuing."
    echo "   Press Enter when ready to continue..."
    read
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Set PYTHONPATH to include the project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the main arbitrage system in background
echo "🔄 Starting arbitrage monitoring system..."
python main.py &
MAIN_PID=$!

# Wait a moment for the main system to initialize
sleep 3

# Start the web UI
echo "🌐 Starting web interface..."
python ui/app.py &
UI_PID=$!

# Save PIDs to file for stop script
echo $MAIN_PID > .main_pid
echo $UI_PID > .ui_pid

echo "✅ System started successfully!"
echo "📊 Main system PID: $MAIN_PID"
echo "🌐 Web UI PID: $UI_PID"
echo "🌍 Web interface available at: http://localhost:5000"
echo ""
echo "📋 To stop the system, run: ./scripts/stop.sh"
echo "📋 To view logs, check the logs/ directory"
echo ""
echo "🔍 Monitoring system status..."
echo "Press Ctrl+C to stop monitoring (system will continue running)"

# Monitor the processes
trap 'echo ""; echo "🛑 Stopping monitoring..."; exit 0' INT
while true; do
    if ! kill -0 $MAIN_PID 2>/dev/null; then
        echo "❌ Main system process stopped unexpectedly"
        break
    fi
    if ! kill -0 $UI_PID 2>/dev/null; then
        echo "❌ Web UI process stopped unexpectedly"
        break
    fi
    sleep 5
done

echo "🔄 System monitoring stopped. Processes may still be running."
echo "   To stop all processes, run: ./scripts/stop.sh" 