from collections import defaultdict
from datetime import datetime

import utils
from indicators.indicators_pool import IndicatorsPool
from trades_storage import TradesStorage
from .deal_filter import DealFilter
from .entities import DealState, DealPhase
from entities import DealConfig, ExitMode, TimeFrame, FilterConfig


class Deal:
    def __init__(
        self,
        config: DealConfig,
        indicators_pool: IndicatorsPool,
        storage: TradesStorage,
        current_state: DealState | None = None
    ):
        self._config = config
        self._indicators_pool = indicators_pool
        self._storage = storage
        self._algorithm = config.trade_algorithm
        self._state = current_state or DealState()
        self._filters: dict[TimeFrame, list[DealFilter]] = defaultdict(list)

        self._init_state()

    def _init_state(self):
        if self._state.phase == DealPhase.LOOK_FOR_ENTRY_POINT:
            self._inti_look_entry_state()
        else:
            self._init_in_deal_state()

    def _create_filters(self, filters_config: list[FilterConfig]):
        for filter_config in filters_config:
            deal_filter = DealFilter(filter_config, self._indicators_pool)
            self._filters[filter_config.timeframe].append(deal_filter)

    def _inti_look_entry_state(self):
        self._create_filters(self._config.entry_condition.filters)

    def _init_in_deal_state(self):
        if self._config.exit_condition.mode == ExitMode.SIGNAL:
            self._create_filters(self._config.exit_condition.signal.filters)

    @property
    def state(self) -> DealState:
        return self._state

    # def get_filters(self, timeframe: TimeFrame) -> list[DealFilter]:
    #     return self._filters[timeframe]

    def check_filters(self, to_timestamp: datetime):
        """
        The function checks the filter condition for closed timeframes according to specified timestamp.
        Args:
            to_timestamp: the timestamp is used to determine the timestamps list
                which filters should be checked for
        """
        for tf in utils.get_closed_timeframes(to_timestamp.timestamp()):
            price = self._storage.get_close_price(tf, to_timestamp)
            for flt in self._filters[tf]:
                flt.check(price)

    def is_triggered(self):
        """
        The property return True if all the filters for all the timeframes are triggered.
        That is the filters' conditions were executed for all these filters.
        Use the function check_filters to check filter condition.
        """
        for tf in self._filters:
            result = all(flt.is_triggered for flt in self._filters[tf])
            if not result:
                return False
        return True
