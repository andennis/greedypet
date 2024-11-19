from entities import FilterConfig, TimeFrame, ConditionOperator
from exceptions import GeneralAppException
from indicators.indicators_pool import IndicatorsPool


class DealFilter:
    def __init__(self, config: FilterConfig, indicators_pool: IndicatorsPool):
        self._condition = config.condition
        self._timeframe = config.time_frame
        self._latest_timestamp = None
        self._indicator = indicators_pool.create_indicator(self._timeframe, config.indicator)

    @property
    def timeframe(self) -> TimeFrame:
        return self._timeframe

    @property
    def periods(self) -> list[int]:
        return self._indicator.periods

    def is_triggered(self, cur_value: float) -> bool:
        latest_result = self._indicator.latest_result
        filter_val = getattr(latest_result, self._condition.name)
        match self._condition.operator:
            case ConditionOperator.GT:
                return cur_value > filter_val
            case ConditionOperator.LT:
                return cur_value < filter_val

        raise GeneralAppException(f"Operator {self._condition.operator} is not supported")
