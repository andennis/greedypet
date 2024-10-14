from unittest.mock import patch, mock_open
from gp_config import load_config
from entities import ExchangeId, MarketType, TradeAlgorithm, FilterType, TimeFrame, ExitMode, ConditionOperator


TEST_CONFIG_FILE_CONTENT = """
---
exchange:
  id: bybit
  api_key: some_key
  api_secret: some_secret
  test_mode: true

market:
  type: spot
  symbol: BTC/USDT

trade_algorithm: long

entry_condition:
  filters:
    - type: BB
      time_frame: 5m

exit_condition:
  mode: signal
  signal:
    filters:
      - type: BB
        time_frame: 15m
      - type: RSI
        time_frame: 15m
        condition:
          operator: gt
          value: 70
    pnl: 2
"""


def test_load_config():
    with patch('builtins.open', mock_open(read_data=TEST_CONFIG_FILE_CONTENT)):
        config = load_config("some_file.yaml")
        assert config
        assert config.exchange
        assert config.exchange.id == ExchangeId.BYBIT
        assert config.exchange.api_key == "some_key"
        assert config.exchange.api_secret == "some_secret"
        assert config.market
        assert config.market.type == MarketType.SPOT
        assert config.market.symbol == "BTC/USDT"
        assert config.trade_algorithm == TradeAlgorithm.LONG
        assert config.entry_condition
        assert config.entry_condition.filters
        assert len(config.entry_condition.filters) == 1
        assert config.entry_condition.filters[0].type == FilterType.BOLLINGER_BENDS
        assert config.entry_condition.filters[0].time_frame == TimeFrame.TF_5M
        assert config.exit_condition
        assert config.exit_condition.mode == ExitMode.SIGNAL
        assert config.exit_condition.signal
        assert config.exit_condition.signal.filters
        assert len(config.exit_condition.signal.filters) == 2
        assert config.exit_condition.signal.filters[1].type == FilterType.RSI
        assert config.exit_condition.signal.filters[1].time_frame == TimeFrame.TF_15M
        assert config.exit_condition.signal.filters[1].condition
        assert config.exit_condition.signal.filters[1].condition.operator == ConditionOperator.GT
        assert config.exit_condition.signal.filters[1].condition.value == 70
