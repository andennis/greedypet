from entities import FilterCondition, ConditionOperator
from exceptions import GeneralAppException
from indicators.base_indicator import BaseIndicator


class DealFilterCondition:
    def __init__(self, config: FilterCondition, indicator: BaseIndicator):
        self._config = config
        self._indicator = indicator

    def check(self, cur_value: float) -> bool:
        latest_result = self._indicator.latest_result
        filter_val = getattr(latest_result, self._config.name)
        match self._config.operator:
            case ConditionOperator.GT:
                return cur_value > filter_val
            case ConditionOperator.LT:
                return cur_value < filter_val

        raise GeneralAppException(f"Operator {self._config.operator} is not supported")
