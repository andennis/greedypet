from deal.deal_filter_condition import DealFilterCondition
from entities import FilterConfig, TimeFrame
from indicators.indicators_pool import IndicatorsPool


class DealFilter:
    def __init__(self, config: FilterConfig, indicators_pool: IndicatorsPool):
        self._timeframe = config.time_frame
        self._latest_timestamp = None
        self._indicator = indicators_pool.create_indicator(self._timeframe, config.indicator)
        self._condition = DealFilterCondition(config.condition, self._indicator)

    @property
    def timeframe(self) -> TimeFrame:
        return self._timeframe

    @property
    def periods(self) -> list[int]:
        return self._indicator.periods

    def is_triggered(self, value: float) -> bool:
        return self._condition.check(value)
