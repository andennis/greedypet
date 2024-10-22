import pandas as pd
from pandas import DataFrame
from pandas.plotting import table

from entities import TimeFrame, TradeSide, StorageConfig, Trade
from utils import timeframe_to_sec


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

    def add_trade(self, trade: Trade):
        for tf, df in self._data.items():
            time_frame_len = timeframe_to_sec(tf) * 1000
            latest_tf = int(df.index[-1].timestamp()) * 1000
            new_tf = trade.timestamp // time_frame_len * time_frame_len
            if new_tf >= latest_tf + time_frame_len:
                new_ts = pd.Timestamp(new_tf, unit="ms")
                df.loc[new_ts] = [trade.price] * 4 + [trade.amount]
            else:
                row = df.loc[df.index[-1]]
                row.high = max(row.high, trade.price)
                row.low = min(row.low, trade.price)
                row.close = trade.price

    def get_latest_ohlcv_data(self, time_frame: TimeFrame, limit: int | None = None) -> DataFrame:
        df = self._data.get(time_frame, DataFrame())
        return df.tail(limit) if limit else df
