import asyncio
from functools import cached_property

from entities import TimeFrame, TradeAlgorithm
from filters.base_filter import BaseFilter
from trades_storage import TradesStorage
from utils import time_to_next_timeframe


class BaseDealTracker:
    def __init__(self, trade_algorithm: TradeAlgorithm, storage: TradesStorage):
        self._trade_algorithm = trade_algorithm
        self._storage = storage

    @property
    def trade_algorithm(self):
        return self._trade_algorithm

    @cached_property
    def timeframe_filters(self) -> dict[TimeFrame, list[BaseFilter]]:
        raise NotImplementedError

    @cached_property
    def min_timeframe(self) -> TimeFrame:
        raise NotImplementedError

    async def sleep_to_next_timeframe(self):
        sleep_interval = time_to_next_timeframe(self.min_timeframe)
        await asyncio.sleep(sleep_interval)

    def apply_filters(self, timestamp: int):
        for tf, filters in self.timeframe_filters.items():
            df = self._storage.get_latest_periods(tf)
            for flt in filters:
                flt.check(timestamp, df)

