from collections import defaultdict
from datetime import datetime

import utils
from entities import IndicatorType, TimeFrame
from indicators.base_indicator import BaseIndicator, BaseIndicatorResult
from indicators.bollinger_bands_indicator import BollingerBandsIndicator
from trades_storage import TradesStorage

IndicatorsMap = dict[TimeFrame, list[BaseIndicator[type[BaseIndicatorResult]]]]


class IndicatorsPool:
    """
    Indicators pool collects the indicators grouped by timeframe
    """
    _INDICATORS_TYPE_MAP: dict[IndicatorType, type[BaseIndicator]] = {
        IndicatorType.BOLLINGER_BENDS: BollingerBandsIndicator
    }

    def __init__(self, storage: TradesStorage):
        self._storage = storage
        self._pool: IndicatorsMap = defaultdict(list)

    @property
    def timeframes(self) -> list[TimeFrame]:
        return list(self._pool)

    def _find_indicator(
        self, timeframe: TimeFrame, indicator_type: IndicatorType
    ) -> BaseIndicator:
        indicator_class = self._INDICATORS_TYPE_MAP[indicator_type]
        indicators = filter(lambda x: type(x) is indicator_class, self._pool[timeframe])
        return next(indicators, None)

    def create_indicator(
        self, timeframe: TimeFrame, indicator_type: IndicatorType
    ) -> BaseIndicator:
        indicator = self._find_indicator(timeframe, indicator_type)
        if indicator:
            return indicator

        indicator_class = self._INDICATORS_TYPE_MAP[indicator_type]
        indicator = indicator_class(self._storage, timeframe)
        self._pool[timeframe].append(indicator)
        return indicator

    def get_indicators(self, timeframe: TimeFrame) -> list[BaseIndicator]:
        return self._pool[timeframe]

    def calculate(self, to_timestamp: datetime) -> None:
        timeframes = utils.get_closed_timeframes(to_timestamp.timestamp())
        for tf in timeframes:
            for indicator in self._pool[tf]:
                indicator.calculate(to_timestamp)
