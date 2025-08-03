#!/bin/bash

# Arbitrage Trading System Stop Script
echo "🛑 Stopping Arbitrage Trading System..."

# Function to stop a process by PID file
stop_process() {
    local pid_file=$1
    local process_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🔄 Stopping $process_name (PID: $pid)..."
            kill "$pid"
            
            # Wait for process to stop
            local count=0
            while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚠️  Force stopping $process_name..."
                kill -9 "$pid"
            fi
            
            echo "✅ $process_name stopped"
        else
            echo "ℹ️  $process_name is not running"
        fi
        rm -f "$pid_file"
    else
        echo "ℹ️  No PID file found for $process_name"
    fi
}

# Stop main system
stop_process ".main_pid" "Main arbitrage system"

# Stop web UI
stop_process ".ui_pid" "Web UI"

# Kill any remaining Python processes related to our system
echo "🧹 Cleaning up any remaining processes..."
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "python.*ui/app.py" 2>/dev/null || true

echo "✅ All processes stopped successfully!"
echo ""
echo "📊 System status:"
echo "   - Main system: Stopped"
echo "   - Web UI: Stopped"
echo "   - Logs available in: logs/ directory"
echo ""
echo "🚀 To restart the system, run: ./scripts/start.sh" 