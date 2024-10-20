import pandas as pd
from entities import TimeFrame, TradeSide
from gp_config import GPConfig


class TradesStorage:
    def __init__(self, config: GPConfig):
        self._config = config
        self._data: dict[TimeFrame, pd.DataFrame] = dict()

    def save_initial_ohlcv_data(self, time_frame: TimeFrame, ohlcv_data: list[list[float]]):
        df = pd.DataFrame(
            ohlcv_data, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        self._data[time_frame] = df

    def add_trade(self, timestamp: int, side: TradeSide, price: float, volume: float):
        pass

    def get_ohlcv(self, time_frame: TimeFrame, limit: int) -> list[list[float]]:
        pass
