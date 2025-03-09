import asyncio
from functools import cached_property

import watchbird.utils as utils
from watchbird.entities import TimeFrame, ExitMode, DealConfig


class MarketDataAnalyzer:
    def __init__(self, config: DealConfig):
        self._config = config

    @cached_property
    def _min_timeframe(self) -> TimeFrame:
        filters = self._config.entry_condition.filters
        min_tf1 = min(map(lambda x: x.timeframe, filters), key=utils.timeframe_to_sec)
        if self._config.exit_condition.mode == ExitMode.SIGNAL:
            min_tf2 = min(
                map(lambda x: x.timeframe, self._config.exit_condition.signal.filters),
                key=utils.timeframe_to_sec,
            )
            min_tf1 = min(min_tf1, min_tf2, key=utils.timeframe_to_sec)

        return min_tf1

    async def sleep_to_next_timeframe(self):
        sleep_interval = utils.get_time_to_next_timeframe(self._min_timeframe)
        await asyncio.sleep(sleep_interval)
