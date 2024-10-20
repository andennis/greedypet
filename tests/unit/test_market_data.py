import pytest
from unittest.mock import patch, call
from market_data_collector import MarketDataCollector
from gp_config import GPConfig
from entities import TimeFrame


@pytest.mark.asyncio
@patch("data_reader.ExchangeDataReader.read_ohlcv_data")
async def test_collect_initial_data(mock_read_ohlcv_data):
    config_data = {
        "exchange": {"id": "bybit"},
        "market": {"symbol": "BTC/USDT"},
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
        },
    }
    config = GPConfig(**config_data)
    data_collector = MarketDataCollector(config)
    mock_read_ohlcv_data.return_value = [[x for x in range(6)]]
    data = await data_collector.collect_initial_data()
    assert data
    assert isinstance(data, dict)
    assert {TimeFrame.TF_5M, TimeFrame.TF_15M, TimeFrame.TF_30M} == set(data.keys())
    assert data[TimeFrame.TF_5M] == [[x for x in range(6)]]
    mock_read_ohlcv_data.assert_has_calls(
        [
            call(config.market.symbol, TimeFrame.TF_5M, 21),
            call(config.market.symbol, TimeFrame.TF_15M, 25),
            call(config.market.symbol, TimeFrame.TF_30M, 16),
        ]
    )
