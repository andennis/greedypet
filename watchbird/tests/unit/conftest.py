import pytest

from watchbird.entities import StorageConfig
from watchbird.trades_storage import TradesStorage


# @pytest.fixture
# def trade_symbol():
#     return "BTC/USDT"


@pytest.fixture
def trades_storage():
    return TradesStorage(StorageConfig())
