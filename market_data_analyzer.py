import asyncio
from functools import cached_property

from black.trans import defaultdict

from entities import TimeFrame, ExitMode, DealConfig
from trades_storage import TradesStorage
from utils import timeframe_to_sec, get_time_to_next_timeframe


class MarketDataAnalyzer:
    def __init__(self, config: DealConfig, storage: TradesStorage):
        self._config = config
        self._storage = storage

    @cached_property
    def timeframe_entrance_filters(self):
        result = defaultdict(list)
        for flt in self._config.entry_condition.filters:
            result[flt.timeframe].append(flt)

        return result

    @cached_property
    def timeframe_exit_filters(self):
        result = defaultdict(list)
        if self._config.exit_condition.mode == ExitMode.SIGNAL:
            for flt in self._config.exit_condition.signal.filters:
                result[flt.timeframe].append(flt)

        return result

    @cached_property
    def min_timeframe(self) -> TimeFrame:
        filters = self._config.entry_condition.filters
        min_tf1 = min(map(lambda x: x.timeframe, filters), key=timeframe_to_sec)
        if self._config.exit_condition.mode == ExitMode.SIGNAL:
            min_tf2 = min(
                map(lambda x: x.timeframe, self._config.exit_condition.signal.filters),
                key=timeframe_to_sec,
            )
            min_tf1 = min(min_tf1, min_tf2, key=timeframe_to_sec)

        return min_tf1

    async def sleep_to_next_timeframe(self):
        sleep_interval = get_time_to_next_timeframe(self.min_timeframe)
        await asyncio.sleep(sleep_interval)
