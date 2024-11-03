import pytest
from unittest.mock import patch, call, AsyncMock
from market_data_collector import MarketDataCollector
from gp_config import GPConfig
from entities import TimeFrame, Trade, TradeSide

_config_data = {
    "exchange": {"id": "bybit"},
    "market": {"symbol": "BTC/USDT"},
    "deal": {
        "entry_condition": {
            "filters": [
                {"type": "BB", "time_frame": "5m", "periods": 21},
                {"type": "BB", "time_frame": "15m", "periods": 22},
                {"type": "RSI", "time_frame": "5m", "periods": 15},
            ]
        },
        "exit_condition": {
            "mode": "signal",
            "signal": {
                "filters": [
                    {"type": "BB", "time_frame": "15m", "periods": 25},
                    {
                        "type": "RSI",
                        "time_frame": "15m",
                        "periods": 15,
                        "condition": {"operator": "gt", "value": 70},
                    },
                    {
                        "type": "RSI",
                        "time_frame": "30m",
                        "periods": 16,
                        "condition": {"operator": "gt", "value": 70},
                    },
                ],
            },
        }
    }
}


@pytest.fixture
def app_config():
    return GPConfig(**_config_data)


@pytest.fixture
def data_collector(app_config):
    return MarketDataCollector(app_config)


@pytest.mark.asyncio
@patch("exchange_data_reader.ExchangeDataReader.read_ohlcv_data")
async def test_collect_initial_data(mock_read_ohlcv_data, data_collector, app_config):
    mock_read_ohlcv_data.return_value = [[x for x in range(6)]]
    data = await data_collector.collect_initial_data()
    assert data
    assert isinstance(data, dict)
    assert {TimeFrame.TF_5M, TimeFrame.TF_15M, TimeFrame.TF_30M} == set(data.keys())
    assert data[TimeFrame.TF_5M] == [[x for x in range(6)]]
    mock_read_ohlcv_data.assert_has_awaits(
        [
            call(app_config.market.symbol, TimeFrame.TF_5M, 21),
            call(app_config.market.symbol, TimeFrame.TF_15M, 25),
            call(app_config.market.symbol, TimeFrame.TF_30M, 16),
        ]
    )


@pytest.mark.asyncio
@patch("exchange_data_reader.ExchangeDataReader.read_latest_trades")
async def test_collect_trades(mock_read_latest_trades: AsyncMock, data_collector):
    trade = Trade(side=TradeSide.BUY, price=1, amount=1, timestamp=123)
    mock_read_latest_trades.return_value = [trade]
    result = await data_collector.collect_trades()
    assert result
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == trade
    mock_read_latest_trades.assert_awaited_once()


@pytest.mark.asyncio
@patch("exchange_data_reader.ExchangeDataReader.close")
async def test_close(mock_close: AsyncMock, data_collector):
    await data_collector.close()
    mock_close.assert_awaited_once()


