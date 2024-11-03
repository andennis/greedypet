from collections import defaultdict
from functools import cached_property

from deal_tracker import BaseDealTracker
from entities import TradeAlgorithm, DealEntryConfig, TimeFrame
from filters.base_filter import BaseFilter
import filters.filter_factory as filter_factory
from trades_storage import TradesStorage
from utils import timeframe_to_sec


class DealEntryTracker(BaseDealTracker):
    def __init__(self, trade_algorithm: TradeAlgorithm, storage: TradesStorage, config: DealEntryConfig):
        super().__init__(trade_algorithm, storage)
        self._config = config

    @cached_property
    def timeframe_filters(self) -> dict[TimeFrame, list[BaseFilter]]:
        result = defaultdict(list)
        for flt_cfg in self._config.filters:
            flt = filter_factory.create_filter(flt_cfg, self.trade_algorithm)
            result[flt.time_frame].append(flt)

        return result

    @cached_property
    def min_timeframe(self) -> TimeFrame:
        return min(map(lambda x: x.time_frame, self._config.filters), key=timeframe_to_sec)
