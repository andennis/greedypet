from typing import TypeVar, Generic

from entities import TimeFrame
from trades_storage import TradesStorage

T = TypeVar("T")


class BaseIndicator(Generic[T]):
    def __init__(self, storage: TradesStorage, timeframe: TimeFrame):
        self._storage = storage
        self._timeframe = timeframe

    def calculate(self, to_timestamp: int) -> T:
        raise NotImplementedError
