from datetime import datetime
import pandas_ta as ta
from dataclasses import dataclass
from watchbird.exceptions import GeneralAppException
from .base_indicator import BaseIndicator, BaseIndicatorResult


@dataclass
class BollingerBandsResult(BaseIndicatorResult):
    upper_value: float
    lower_value: float


class BollingerBandsIndicator(BaseIndicator[BollingerBandsResult]):
    _PERIODS = 20

    @property
    def periods(self):
        return self._PERIODS

    def calculate(self, to_timestamp: datetime) -> BollingerBandsResult:
        if self._last_result and self._last_result.timestamp == to_timestamp:
            return self._last_result

        df = self._storage.get_latest_periods(
            self._timeframe, to_timestamp=to_timestamp, limit=self._PERIODS
        )
        if len(df) < self._PERIODS:
            raise GeneralAppException(
                f"Number of periods {len(df)} is not enough to calculate BB indicator"
            )

        bb = ta.bbands(df["close"], length=self._PERIODS, std=2)
        row = bb.iloc[-1]
        self._last_result = BollingerBandsResult(
            timestamp=to_timestamp,
            upper_value=row["BBU_20_2.0"],
            lower_value=row["BBL_20_2.0"],
        )
        return self._last_result
