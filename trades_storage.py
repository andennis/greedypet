import pandas as pd
from pandas import DataFrame

from entities import TimeFrame, TradeSide, StorageConfig


class TradesStorage:
    def __init__(self, config: StorageConfig, symbol: str):
        self._config = config
        self._symbol = symbol
        self._data: dict[TimeFrame, pd.DataFrame] = dict()

    def upload_initial_ohlcv_data(self, time_frame: TimeFrame, ohlcv_data: list[list[float]]) -> DataFrame:
        df = pd.DataFrame(
            ohlcv_data, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        self._data[time_frame] = df
        return df

    def add_trade(self, timestamp: int, side: TradeSide, price: float, volume: float):
        pass

    def get_latest_ohlcv_data(self, time_frame: TimeFrame, limit: int | None = None) -> DataFrame:
        df = self._data.get(time_frame, DataFrame())
        return df.tail(limit) if limit else df
