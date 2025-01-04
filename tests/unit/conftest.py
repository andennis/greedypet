import pytest

from entities import StorageConfig
from trades_storage import TradesStorage


# @pytest.fixture
# def trade_symbol():
#     return "BTC/USDT"


@pytest.fixture
def trades_storage():
    return TradesStorage(StorageConfig())
