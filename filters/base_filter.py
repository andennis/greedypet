from pandas import DataFrame
from entities import FilterConfig, TimeFrame, TradeAlgorithm, IndicatorType


class BaseFilter:
    def __init__(self, config: FilterConfig):
        self._time_frame = config.time_frame
        self._latest_timestamp = None

    @property
    def time_frame(self) -> TimeFrame:
        return self._time_frame

    @property
    def periods(self) -> int:
        raise NotImplementedError

    @property
    def all_periods(self) -> list[int]:
        return [self.periods]

    @property
    def is_signal(self) -> bool:
        raise NotImplementedError

    def check(self, timestamp: int, df: DataFrame) -> None:
        raise NotImplementedError
    