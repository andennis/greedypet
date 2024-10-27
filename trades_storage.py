import pandas as pd
from pandas import DataFrame
from dataclasses import dataclass

from exceptions import GeneralAppException

from entities import TimeFrame, StorageConfig, Trade
from utils import timeframe_to_sec


@dataclass
class _TimeFrameData:
    data: DataFrame
    data_len: int
    latest_trade_timestamp: int


class TradesStorage:
    _COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]

    def __init__(self, config: StorageConfig, symbol: str):
        self._config = config
        self._symbol = symbol
        self._data: dict[TimeFrame, _TimeFrameData] = dict()

    def upload_initial_ohlcv_data(
        self, time_frame: TimeFrame, ohlcv_data: list[list[float]]
    ) -> DataFrame:
        if not ohlcv_data:
            raise GeneralAppException("No data provided")
        if len(ohlcv_data[0]) != len(self._COLUMNS):
            raise GeneralAppException("Wrong data structure")

        df = pd.DataFrame(ohlcv_data, columns=self._COLUMNS)
        ts_col = self._COLUMNS[0]
        df[ts_col] = pd.to_datetime(df[ts_col], unit="ms")
        df.set_index(ts_col, inplace=True)
        self._data[time_frame] = _TimeFrameData(
            data=df,
            data_len=len(df),
            latest_trade_timestamp=int(df.index[-1].timestamp()) * 1000,
        )
        return df

    def add_trade(self, trade: Trade):
        for tf, dfd in self._data.items():
            df = dfd.data
            time_frame_len = timeframe_to_sec(tf) * 1000
            latest_tf = int(df.index[-1].timestamp()) * 1000
            new_tf = trade.timestamp // time_frame_len * time_frame_len
            if new_tf >= latest_tf + time_frame_len:
                # Add new row
                new_ts = pd.Timestamp(new_tf, unit="ms")
                df.loc[new_ts] = (
                    [df.iloc[-1].close] + [trade.price] * 3 + [trade.amount]
                )
                # Remove first row
                if len(df) > dfd.data_len:
                    df.drop(df.index[0], inplace=True)
            elif new_tf >= latest_tf:
                row = df.loc[df.index[-1]]
                row.high = max(row.high, trade.price)
                row.low = min(row.low, trade.price)
                if trade.timestamp > dfd.latest_trade_timestamp:
                    row.close = trade.price
                row.volume += trade.amount
            else:
                trade_ts = pd.Timestamp(trade.timestamp, unit="ms")
                raise GeneralAppException(
                    f"Trade timestamp:{trade_ts} is less than latest timeframe:{df.index[-1]}"
                )
            if trade.timestamp > dfd.latest_trade_timestamp:
                dfd.latest_trade_timestamp = trade.timestamp

    def get_latest_timeframes(
        self, time_frame: TimeFrame, limit: int | None = None
    ) -> DataFrame:
        if time_frame not in self._data:
            raise GeneralAppException(f"Timeframe {time_frame} does not exist")

        df = self._data[time_frame].data
        return df.tail(limit) if limit else df
