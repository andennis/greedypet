from unittest.mock import patch, PropertyMock, Mock
import pytest
from entities import DealConfig, TimeFrame
from market_data_analyzer import MarketDataAnalyzer
from tests.unit.conftest import trades_storage

_deal_config = {
    "entry_condition": {
        "filters": [
            {"type": "BB", "time_frame": "5m", "periods": 21},
            {"type": "BB", "time_frame": "30m", "periods": 22},
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


@pytest.fixture
def deal_config():
    return DealConfig(**_deal_config)


@pytest.fixture
def data_analyzer(deal_config, trades_storage):
    return MarketDataAnalyzer(deal_config, trades_storage)


@pytest.mark.parametrize(
    "time_frame, result",
    [
        (TimeFrame.TF_5M, TimeFrame.TF_5M),
        (TimeFrame.TF_1M, TimeFrame.TF_1M),
        (TimeFrame.TF_1H, TimeFrame.TF_15M),
    ],
)
def test_min_timeframe(
    deal_config, data_analyzer, time_frame: TimeFrame, result: TimeFrame
):
    deal_config.entry_condition.filters[0].time_frame = time_frame
    deal_config.entry_condition.filters[2].time_frame = time_frame
    assert data_analyzer.min_timeframe == result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cur_time, time_frame, sleep_time", [
        (600, TimeFrame.TF_1M, 60),
        (601, TimeFrame.TF_1M, 59),
        (659, TimeFrame.TF_1M, 1),
        (600, TimeFrame.TF_5M, 5 * 60),
        (600 + 150, TimeFrame.TF_5M, 5 * 60 - 150),
        (3600, TimeFrame.TF_15M, 15 * 60),
        (3600 + 600, TimeFrame.TF_15M, 15 * 60 - 600),
    ]
)
@patch(
    "market_data_analyzer.MarketDataAnalyzer.min_timeframe", new_callable=PropertyMock
)
@patch("market_data_analyzer.asyncio.sleep")
@patch("market_data_analyzer.time.time")
async def test_sleep_to_next_timeframe(
    mock_time,
    mock_sleep,
    mock_min_timeframe,
    data_analyzer,
    cur_time: int,
    time_frame: TimeFrame,
    sleep_time: int,
):
    mock_min_timeframe.return_value = time_frame
    mock_time.return_value = cur_time
    await data_analyzer.sleep_to_next_timeframe()
    mock_sleep.assert_awaited_once_with(sleep_time)
