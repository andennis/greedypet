from deal.deal_filter_condition import DealFilterCondition
from entities import FilterConfig, TimeFrame
from indicators.indicators_pool import IndicatorsPool


class DealFilter:
    def __init__(self, config: FilterConfig, indicators_pool: IndicatorsPool):
        self._timeframe = config.timeframe
        self._latest_timestamp = None
        self._indicator = indicators_pool.create_indicator(self._timeframe, config.indicator)
        self._condition = DealFilterCondition(config.condition, self._indicator)
        self._is_triggered = False

    # @property
    # def timeframe(self) -> TimeFrame:
    #     return self._timeframe

    # def reset(self):
    #     self._is_triggered = False

    def is_triggered(self) -> bool:
        return self._is_triggered

    def check(self, signal_value: float):
        self._is_triggered = self._condition.check(signal_value)

