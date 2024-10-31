import time
import asyncio
from functools import cached_property
from entities import TimeFrame, ExitMode, DealConfig
from trades_storage import TradesStorage
from utils import timeframe_to_sec


class MarketDataAnalyzer:
    def __init__(self, config: DealConfig, storage: TradesStorage):
        self._config = config
        self._storage = storage

    @cached_property
    def min_timeframe(self) -> TimeFrame:
        filters = self._config.entry_condition.filters
        if self._config.exit_condition.mode == ExitMode.SIGNAL:
            filters.extend(self._config.exit_condition.signal.filters)

        return min(map(lambda x: x.time_frame, filters), key=timeframe_to_sec)

    async def sleep_to_next_timeframe(self):
        tf = timeframe_to_sec(self.min_timeframe)
        cur_time = int(time.time())
        next_tf = cur_time // tf * tf + tf
        await asyncio.sleep(next_tf - cur_time)
