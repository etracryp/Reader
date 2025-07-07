import pytest
import asyncio
from utils.fees import get_all_fees

pytestmark = pytest.mark.asyncio

async def test_get_all_fees():
    fees = await get_all_fees()
    assert isinstance(fees, dict)
    assert 'cex' in fees
    assert 'gate' in fees
    assert 'binance' in fees
    # Each should be a dict or error
    for ex in ['cex', 'gate', 'binance']:
        assert isinstance(fees[ex], (dict, list)), f"{ex} fees should be dict or list, got {type(fees[ex])}" 