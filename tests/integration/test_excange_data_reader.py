import pytest
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
