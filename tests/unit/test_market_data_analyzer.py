from unittest.mock import patch
import pytest
from entities import DealConfig, TimeFrame
from market_data_analyzer import MarketDataAnalyzer

_deal_config = {
    "trade_algorithm": "long",
    "entry_condition": {
        "filters": [
            {
                "indicator": "BB",
                "timeframe": "5m",
                "condition": {
                     "operator": "lt", "name": "lower_value"
                }
            },
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
                },
            ],
        },
    },
}


@pytest.fixture
def deal_config():
    return DealConfig(**_deal_config)


@pytest.fixture
def data_analyzer(deal_config):
    return MarketDataAnalyzer(deal_config)


@pytest.mark.asyncio
@patch("market_data_analyzer.asyncio.sleep")
@patch("utils.get_time_to_next_timeframe")
async def test_sleep_to_next_timeframe(
    mock_time_to_next_timeframe,
    mock_sleep,
    data_analyzer,
):
    mock_time_to_next_timeframe.return_value = 15
    await data_analyzer.sleep_to_next_timeframe()
    mock_time_to_next_timeframe.assert_called_once_with(TimeFrame.TF_5M)
    mock_sleep.assert_awaited_once_with(15)

