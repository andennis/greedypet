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
        load_config("some_file.yaml")

        from gp_config import GP_CONFIG
        global GP_CONFIG
        assert GP_CONFIG
        assert GP_CONFIG.exchange
        assert GP_CONFIG.exchange.id == ExchangeId.BYBIT
        assert GP_CONFIG.exchange.api_key == "some_key"
        assert GP_CONFIG.exchange.api_secret == "some_secret"
        assert GP_CONFIG.market
        assert GP_CONFIG.market.type == MarketType.SPOT
        assert GP_CONFIG.market.symbol == "BTC/USDT"
        assert GP_CONFIG.trade_algorithm == TradeAlgorithm.LONG
        assert GP_CONFIG.entry_condition
        assert GP_CONFIG.entry_condition.filters
        assert len(GP_CONFIG.entry_condition.filters) == 1
        assert GP_CONFIG.entry_condition.filters[0].type == FilterType.BOLLINGER_BENDS
        assert GP_CONFIG.entry_condition.filters[0].time_frame == TimeFrame.TF_5M
        assert GP_CONFIG.exit_condition
        assert GP_CONFIG.exit_condition.mode == ExitMode.SIGNAL
        assert GP_CONFIG.exit_condition.signal
        assert GP_CONFIG.exit_condition.signal.filters
        assert len(GP_CONFIG.exit_condition.signal.filters) == 2
        assert GP_CONFIG.exit_condition.signal.filters[1].type == FilterType.RSI
        assert GP_CONFIG.exit_condition.signal.filters[1].time_frame == TimeFrame.TF_15M
        assert GP_CONFIG.exit_condition.signal.filters[1].condition
        assert GP_CONFIG.exit_condition.signal.filters[1].condition.operator == ConditionOperator.GT
        assert GP_CONFIG.exit_condition.signal.filters[1].condition.value == 70
