import pytest
from unittest.mock import patch, call, AsyncMock

from indicators.indicators_pool import IndicatorsPool
from market_data_collector import MarketDataCollector
from gp_config import GPConfig
from entities import TimeFrame, Trade, TradeSide, IndicatorType

_config_data = {
    "exchange": {"id": "bybit"},
    "market": {"type": "spot", "symbol": "BTC/USDT"},
    "deal": {
        "trade_algorithm": "long",
        "entry_condition": {
            "filters": [
                {
                    "indicator": "BB",
                    "timeframe": "5m",
                    "condition": {
                        "operator": "lt", "name": "lower_value"
                    }
                }
            ]
        },
        "exit_condition": {
            "mode": "signal",
            "signal": {
                "filters": [
                    {
                        "indicator": "BB",
                        "timeframe": "15m",
                        "condition": {
                            "operator": "gt", "name": "upper_value"
                        }
                    }
               ]
            }
        }
    }
}


@pytest.fixture()
def app_config():
    return GPConfig(**_config_data)


@pytest.fixture
def data_collector(app_config, trades_storage):
    pool = IndicatorsPool(trades_storage)
    pool.create_indicator(TimeFrame.TF_5M, IndicatorType.BOLLINGER_BENDS)
    pool.create_indicator(TimeFrame.TF_15M, IndicatorType.BOLLINGER_BENDS)
    return MarketDataCollector(app_config.exchange, app_config.market.symbol, pool)


@pytest.mark.asyncio
@patch("exchange_data_reader.ExchangeDataReader.read_ohlcv_data")
async def test_collect_initial_data(mock_read_ohlcv_data, data_collector, app_config):
    mock_read_ohlcv_data.return_value = [[x for x in range(6)]]
    data = await data_collector.collect_initial_data()
    assert data
    assert isinstance(data, dict)
    assert {TimeFrame.TF_5M, TimeFrame.TF_15M} == set(data.keys())
    assert data[TimeFrame.TF_5M] == [[x for x in range(6)]]
    mock_read_ohlcv_data.assert_has_awaits(
        [
            call(app_config.market.symbol, TimeFrame.TF_5M, 21),
            call(app_config.market.symbol, TimeFrame.TF_15M, 21),
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
