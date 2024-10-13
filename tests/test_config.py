from unittest.mock import patch, mock_open
from gp_config import load_config


TEST_CONFIG = """
---
exchange:
  name: bybit
  api_key: some_key
  api_secret: some_secret
  test_mode: true

market:
  type: spot
  symbol: FTM/USDT

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
    with patch('builtins.open', mock_open(read_data=TEST_CONFIG)):
        load_config("some_file.yaml")

        from gp_config import GP_CONFIG
        global GP_CONFIG
        assert GP_CONFIG
        assert GP_CONFIG.exchange
        assert GP_CONFIG.exchange.name == "bybit"
