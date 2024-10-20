from .base_filter import BaseFilter
from entities import Filter, MovingAverageType


class BollingerBendsFilter(BaseFilter):
    _DEF_PERIODS = 20

    def __init__(self, filter_config: Filter):
        super().__init__(filter_config)
        self._periods = filter_config.periods or self._DEF_PERIODS
        self._moving_average = filter_config.moving_average or MovingAverageType.SMA

    @property
    def periods(self):
        return self._periods

    @property
    def moving_average(self) -> MovingAverageType:
        return self._moving_average
