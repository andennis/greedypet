from unittest.mock import patch, mock_open
import pytest

from gp_config import load_config
from entities import (
    ExchangeId,
    MarketType,
    TradeAlgorithm,
    IndicatorType,
    TimeFrame,
    ExitMode,
    ConditionOperator,
    MovingAverageType,
    TradingMode, DealExitConfig,
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
        - type: BB
          time_frame: 5m
          periods: 21
    
    exit_condition:
      mode: signal
      signal:
        filters:
          - type: BB
            time_frame: 15m
            moving_average: ema
            periods: 20
          - type: RSI
            time_frame: 15m
            condition:
              operator: gt
              value: 70
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
        assert config.exchange.trading_mode == TradingMode.DEMO
        assert config.market
        assert config.market.indicator == MarketType.SPOT
        assert config.market.symbol == "BTC/USDT"
        assert config.deal
        assert config.deal.trade_algorithm == TradeAlgorithm.LONG
        assert config.deal.entry_condition
        assert config.deal.entry_condition.filters
        assert len(config.deal.entry_condition.filters) == 1
        assert config.deal.entry_condition.filters[0].indicator == IndicatorType.BOLLINGER_BENDS
        assert config.deal.entry_condition.filters[0].time_frame == TimeFrame.TF_5M
        # assert config.deal.entry_condition.filters[0].periods == 21
        # assert not config.deal.entry_condition.filters[0].moving_average
        assert config.deal.exit_condition
        assert config.deal.exit_condition.mode == ExitMode.SIGNAL
        assert config.deal.exit_condition.signal
        assert config.deal.exit_condition.signal.filters
        assert len(config.deal.exit_condition.signal.filters) == 2
        # assert config.deal.exit_condition.signal.filters[0].periods == 20
        # assert config.deal.exit_condition.signal.filters[0].moving_average == MovingAverageType.EMA
        assert config.deal.exit_condition.signal.filters[1].indicator == IndicatorType.RSI
        assert config.deal.exit_condition.signal.filters[1].time_frame == TimeFrame.TF_15M
        assert config.deal.exit_condition.signal.filters[1].condition
        assert (
            config.deal.exit_condition.signal.filters[1].condition.operator
            == ConditionOperator.GT
        )
        assert config.deal.exit_condition.signal.filters[1].condition.value == 70


def test_exit_condition_validator():
    with pytest.raises(ValueError):
        DealExitConfig(mode=ExitMode.SIGNAL, signal=None)
