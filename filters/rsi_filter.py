from .base_filter import BaseFilter
from entities import Filter


class RSIFilter(BaseFilter):
    _DEF_PERIODS = 14

    def __init__(self, filter_config: Filter):
        super().__init__(filter_config)
        self._periods = filter_config.periods or self._DEF_PERIODS

    @property
    def periods(self):
        return self._periods
