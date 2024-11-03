from entities import FilterConfig, TimeFrame, TradeAlgorithm


class BaseFilter:
    # The FilterType must be assigned in derivative class
    _FILTER_TYPE = None

    def __init__(self, config: FilterConfig, trade_algorithm: TradeAlgorithm):
        self._time_frame = config.time_frame
        self._trade_algorithm = trade_algorithm
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

    def apply(self, timestamp: int) -> None:
        raise NotImplementedError
    