import pytest
from pycares import symbol

from data_reader import ExchangeDataReader
from entities import TimeFrame


@pytest.mark.asyncio
async def test_read_ohlcv_data(data_reader: ExchangeDataReader):
    limit = 3
    result = await data_reader.read_ohlcv_data("BTC/USDT", TimeFrame.TF_1H, limit)
    assert result
    assert isinstance(result, list)
    assert len(result) == limit
    assert len(result[0]) == 6


@pytest.mark.asyncio
async def test_read_latest_trades(data_reader: ExchangeDataReader):
    result = await data_reader.read_latest_trades("BTC/USDT")
    assert result
    assert result[0].price > 0
    assert result[0].amount > 0
