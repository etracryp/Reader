# Placeholder for fee calculation utilities 

import asyncio
from exchanges import cex, gate, binance

async def get_all_fees():
    """Fetch spot trading fees from all exchanges and return as a dict."""
    cex_fees, gate_fees, binance_fees = await asyncio.gather(
        cex.get_fees(),
        gate.get_fees(),
        binance.get_fees()
    )
    return {
        'cex': cex_fees,
        'gate': gate_fees,
        'binance': binance_fees
    }

if __name__ == '__main__':
    async def main():
        all_fees = await get_all_fees()
        for ex, fees in all_fees.items():
            print(f"{ex.upper()} fees:", fees)
    asyncio.run(main()) 