from datetime import datetime
from typing import TypeVar, Generic
from dataclasses import dataclass

from watchbird.entities import TimeFrame
from watchbird.trades_storage import TradesStorage


@dataclass
class BaseIndicatorResult:
    timestamp: datetime


T_co = TypeVar("T_co", bound=BaseIndicatorResult, covariant=True)


class BaseIndicator(Generic[T_co]):
    def __init__(self, storage: TradesStorage, timeframe: TimeFrame):
        self._storage = storage
        self._timeframe = timeframe
        self._last_result: T_co | None = None

    @property
    def periods(self):
        raise NotImplementedError

    @property
    def latest_result(self) -> T_co:
        return self._last_result

    def calculate(self, to_timestamp: datetime) -> T_co:
        raise NotImplementedError
