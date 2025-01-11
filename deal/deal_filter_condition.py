from entities import FilterCondition, ConditionOperator
from exceptions import GeneralAppException
from indicators.base_indicator import BaseIndicator


class DealFilterCondition:
    def __init__(self, config: FilterCondition, indicator: BaseIndicator):
        self._config = config
        self._indicator = indicator

    def check(self, cur_value: float) -> bool:
        latest_result = self._indicator.latest_result
        indicator_val = getattr(latest_result, self._config.name)
        val = self._config.value or cur_value
        match self._config.operator:
            case ConditionOperator.GT:
                return indicator_val > val
            case ConditionOperator.LT:
                return indicator_val < val

        raise GeneralAppException(f"Operator {self._config.operator} is not supported")
