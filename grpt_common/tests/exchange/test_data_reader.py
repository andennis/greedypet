import pytest
from unittest.mock import patch, AsyncMock

from grpt_common.exchange.data_reader import ExchangeDataReader
from grpt_common.exchange.entities import ExchangeConfig, ExchangeId, TimeFrame, ExchangeTrade, ExchangeTradeSide


@pytest.fixture
def data_reader() -> ExchangeDataReader:
    return ExchangeDataReader(ExchangeConfig(id=ExchangeId.BYBIT))


def test_data_reader_config():
    config = ExchangeConfig(
        id=ExchangeId.BYBIT,
        max_retries_on_failure=5,
        max_retries_on_failure_delay=555
    )
    dr = ExchangeDataReader(config)
    assert dr.exchange.id == "bybit"
    assert not dr.exchange.isSandboxModeEnabled
    assert dr.exchange.options["maxRetriesOnFailure"] == 5
    assert dr.exchange.options["maxRetriesOnFailureDelay"] == 555


@pytest.mark.asyncio
async def test_read_ohlcv_data(data_reader: ExchangeDataReader):
    limit = 3
    with patch.object(
        data_reader._exchange, "fetch_mark_ohlcv"
    ) as mock_fetch_mark_ohlcv:
        mock_fetch_mark_ohlcv.side_effect = AsyncMock(
            return_value=[[0] * 6 for _ in range(limit)]
        )
        result = await data_reader.read_ohlcv_data("BTC/USDT", TimeFrame.TF_1H, limit)
        assert result
        assert isinstance(result, list)
        assert len(result) == limit
        assert len(result[0]) == 6
        mock_fetch_mark_ohlcv.assert_awaited_once_with(
            "BTC/USDT", timeframe=TimeFrame.TF_1H.value, limit=limit
        )


@pytest.mark.asyncio
async def test_read_latest_trades(data_reader: ExchangeDataReader):
    with patch.object(data_reader._exchange, "watch_trades") as mock_watch_trades:
        tr = dict(symbol="BTC/USDT", side="buy", price=1, amount=2, timestamp=123)
        mock_watch_trades.side_effect = AsyncMock(return_value=[tr])
        result = await data_reader.read_latest_trades(["BTC/USDT"])
        assert result
        assert isinstance(result, list)
        assert isinstance(result[0], ExchangeTrade)
        assert result[0].symbol == tr["symbol"]
        assert result[0].side == ExchangeTradeSide.BUY
        assert result[0].price == tr["price"]
        assert result[0].amount == tr["amount"]
        assert result[0].timestamp == tr["timestamp"]
