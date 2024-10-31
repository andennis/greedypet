import pytest

from entities import StorageConfig
from trades_storage import TradesStorage


@pytest.fixture
def symbol():
    return "BTC/USDT"


@pytest.fixture
def trades_storage(symbol: str):
    return TradesStorage(StorageConfig(), symbol)
