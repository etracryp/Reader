#!/bin/bash

# Arbitrage Trading System Status Script
echo "📊 Arbitrage Trading System Status"
echo "=================================="

# Function to check process status
check_process() {
    local pid_file=$1
    local process_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "✅ $process_name: Running (PID: $pid)"
            return 0
        else
            echo "❌ $process_name: Not running (stale PID file)"
            return 1
        fi
    else
        echo "❌ $process_name: Not running (no PID file)"
        return 1
    fi
}

# Check main system
main_running=false
if check_process ".main_pid" "Main arbitrage system"; then
    main_running=true
fi

# Check web UI
ui_running=false
if check_process ".ui_pid" "Web UI"; then
    ui_running=true
fi

echo ""
echo "🌐 Web Interface Status:"
if [ "$ui_running" = true ]; then
    echo "   ✅ Available at: http://localhost:5000"
    echo "   📊 Check exchange status and price differences"
else
    echo "   ❌ Not running"
fi

echo ""
echo "📁 Log Files:"
if [ -d "logs" ]; then
    echo "   📂 Logs directory: logs/"
    if [ -f "logs/arbitrage_system.log" ]; then
        echo "   📄 Main log: logs/arbitrage_system.log"
    fi
else
    echo "   ❌ Logs directory not found"
fi

echo ""
echo "⚙️ Environment:"
if [ -f ".env" ]; then
    echo "   ✅ Environment file: .env"
else
    echo "   ❌ Environment file missing"
fi

if [ -d "venv" ]; then
    echo "   ✅ Virtual environment: venv/"
else
    echo "   ❌ Virtual environment missing"
fi

echo ""
echo "🔧 Quick Actions:"
echo "   🚀 Start system: ./scripts/start.sh"
echo "   🛑 Stop system: ./scripts/stop.sh"
echo "   🔄 Restart: ./scripts/stop.sh && ./scripts/start.sh"

echo ""
if [ "$main_running" = true ] && [ "$ui_running" = true ]; then
    echo "🎉 System is running normally!"
elif [ "$main_running" = true ]; then
    echo "⚠️  Main system running, but Web UI is down"
elif [ "$ui_running" = true ]; then
    echo "⚠️  Web UI running, but main system is down"
else
    echo "❌ System is not running"
fi 