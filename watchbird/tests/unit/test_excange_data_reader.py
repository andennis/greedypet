import pytest
from unittest.mock import patch, AsyncMock

from watchbird.exchange_data_reader import ExchangeDataReader
from watchbird.entities import ExchangeConfig, ExchangeId, TimeFrame, Trade, TradeSide


@pytest.fixture
def data_reader() -> ExchangeDataReader:
    return ExchangeDataReader(ExchangeConfig(id=ExchangeId.BYBIT))


def test_data_reader_config():
    config = ExchangeConfig(id=ExchangeId.BYBIT, api_key="key1", api_secret="secret1")
    dr = ExchangeDataReader(config)
    assert dr.exchange.id == "bybit"
    assert dr.exchange.apiKey == "key1"
    assert dr.exchange.secret == "secret1"
    # assert dr.exchange.options["sandboxMode"]
    assert dr.exchange.isSandboxModeEnabled


def test_data_reader_config_env(monkeypatch):
    monkeypatch.setenv("GP_API_KEY", "key_env")
    monkeypatch.setenv("GP_API_SECRET", "secret_env")
    config = ExchangeConfig(id=ExchangeId.BYBIT, api_key="key1", api_secret="secret1")
    dr = ExchangeDataReader(config)
    assert dr.exchange.apiKey == "key_env"
    assert dr.exchange.secret == "secret_env"


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
        tr = dict(side="buy", price=1, amount=2, timestamp=123)
        mock_watch_trades.side_effect = AsyncMock(return_value=[tr])
        result = await data_reader.read_latest_trades("BTC/USDT")
        assert result
        assert isinstance(result, list)
        assert isinstance(result[0], Trade)
        assert result[0].side == TradeSide.BUY
        assert result[0].price == 1
        assert result[0].amount == 2
        assert result[0].timestamp == 123
