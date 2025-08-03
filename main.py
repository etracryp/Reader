#!/usr/bin/env python3
"""
Multi-Exchange Arbitrage Trading System
Main entry point for the arbitrage system
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.price_monitor import PriceMonitor
from services.arbitrage_engine import ArbitrageEngine
from services.order_manager import OrderManager
from services.safety_controller import SafetyController

async def main():
    """Main function to start the arbitrage trading system"""
    print("🚀 Multi-Exchange Arbitrage Trading System starting...")
    
    try:
        # Initialize services
        price_monitor = PriceMonitor()
        arbitrage_engine = ArbitrageEngine()
        order_manager = OrderManager()
        safety_controller = SafetyController()
        
        print("✅ All services initialized successfully")
        
        # Set up callbacks
        def on_opportunity(opportunity):
            print(f"🎯 Arbitrage opportunity detected: {opportunity}")
            # Here you would typically submit the opportunity to order manager
            # asyncio.create_task(order_manager.submit_arbitrage_opportunity(opportunity, amount=0.01))
        
        arbitrage_engine.set_opportunity_callback(on_opportunity)
        
        # Start the price monitor
        print("📊 Starting price monitoring...")
        await price_monitor.start()
        
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"❌ Error in main system: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 System stopped")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1) 