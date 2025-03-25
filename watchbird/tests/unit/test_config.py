from unittest.mock import patch, mock_open
import pytest

from watchbird.gp_config import load_config
from watchbird.entities import (
    ExchangeId,
    MarketType,
    TradeAlgorithm,
    IndicatorType,
    TimeFrame,
    ExitMode,
    ConditionOperator,
    ExchangeMode, DealExitConfig,
)


TEST_CONFIG_FILE_CONTENT = """
---
exchange:
  id: bybit
  api_key: some_key
  api_secret: some_secret
  trading_mode: demo

market:
  type: spot
  symbol: BTC/USDT

deal:
    trade_algorithm: long
    
    entry_condition:
      filters:
        - indicator: BB
          timeframe: 5m
          condition:
            operator: lt
            name: "lower_value"
    
    exit_condition:
      mode: signal
      signal:
        filters:
          - indicator: BB
            timeframe: 15m
            condition:
              operator: gt
              name: "upper_value"
        pnl: 2
"""


def test_load_config():
    with patch("builtins.open", mock_open(read_data=TEST_CONFIG_FILE_CONTENT)):
        config = load_config("some_file.yaml")
        assert config
        assert config.exchange
        assert config.exchange.id == ExchangeId.BYBIT
        assert config.exchange.api_key == "some_key"
        assert config.exchange.api_secret == "some_secret"
        assert config.exchange.trading_mode == ExchangeMode.DEMO
        assert config.market
        assert config.market.type == MarketType.SPOT
        assert config.market.symbol == "BTC/USDT"
        assert config.deal
        assert config.deal.trade_algorithm == TradeAlgorithm.LONG

        assert config.deal.entry_condition
        assert config.deal.entry_condition.filters
        assert config.deal.entry_condition.filters[0].indicator == IndicatorType.BOLLINGER_BENDS
        assert config.deal.entry_condition.filters[0].timeframe == TimeFrame.TF_5M
        assert config.deal.entry_condition.filters[0].condition
        assert (
            config.deal.entry_condition.filters[0].condition.operator
            == ConditionOperator.LT
        )
        assert config.deal.entry_condition.filters[0].condition.name == "lower_value"

        assert config.deal.exit_condition
        assert config.deal.exit_condition.mode == ExitMode.SIGNAL
        assert config.deal.exit_condition.signal
        assert config.deal.exit_condition.signal.filters
        assert config.deal.exit_condition.signal.filters[0].indicator == IndicatorType.BOLLINGER_BENDS
        assert config.deal.exit_condition.signal.filters[0].timeframe == TimeFrame.TF_15M
        assert config.deal.exit_condition.signal.filters[0].condition
        assert (
            config.deal.exit_condition.signal.filters[0].condition.operator
            == ConditionOperator.GT
        )
        assert config.deal.exit_condition.signal.filters[0].condition.name == "upper_value"


def test_exit_condition_validator():
    with pytest.raises(ValueError):
        DealExitConfig(mode=ExitMode.SIGNAL, signal=None)
