import pandas_ta as ta
from dataclasses import dataclass
from entities import TimeFrame
from exceptions import GeneralAppException
from indicators.base_indicator import BaseIndicator
from trades_storage import TradesStorage
from utils import timeframe_to_sec


@dataclass
class BollingerBandsResult:
    upper_value: float
    lower_value: float


class BollingerBandsIndicator(BaseIndicator[BollingerBandsResult]):
    _PERIODS = 20

    def __init__(self, storage: TradesStorage, timeframe: TimeFrame):
        super().__init__(storage, timeframe)
        self._timeframe_size = timeframe_to_sec(self._timeframe)

    def calculate(self, to_timestamp: int) -> BollingerBandsResult:
        if to_timestamp % self._timeframe_size:
            raise GeneralAppException(
                f"to_timestamp {to_timestamp} does not correspond to timeframe {self._timeframe.value}"
            )
        df = self._storage.get_latest_periods(self._timeframe, limit=self._PERIODS)
        bb = ta.bbands(df['close'], length=self._PERIODS, std=2)
        row = bb.iloc[-2]
        return BollingerBandsResult(upper_value=row["BBU_20_2.0"], lower_value=row["BBL_20_2.0"])
