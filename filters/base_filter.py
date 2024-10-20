from entities import FilterType, Filter, TimeFrame


class BaseFilter:
    def __init__(self, filter_config: Filter):
        self._type = filter_config.type
        self._time_frame = filter_config.time_frame

    @property
    def filter_type(self) -> FilterType:
        return self._type

    @property
    def time_frame(self) -> TimeFrame:
        return self._time_frame

    @property
    def periods(self) -> int:
        raise NotImplementedError

    @property
    def all_periods(self) -> list[int]:
        return [self.periods]
