from datetime import datetime
import pandas as pd
from pandas import DataFrame
from dataclasses import dataclass

from exceptions import GeneralAppException

from entities import TimeFrame, StorageConfig, Trade, OhlcvData
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
        self, time_frame: TimeFrame, ohlcv_data: OhlcvData
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

    def get_latest_periods(
        self, time_frame: TimeFrame, to_timestamp: datetime | None = None, limit: int | None = None
    ) -> DataFrame:
        """
        The function returns the latest ohlcv data for specified timeframe.
        The initial date for the specified timeframe must be preliminarily uploaded
        by the function upload_initial_ohlcv_data

        Args:
            time_frame (TimeFrame): the ohlcv data timeframe
            to_timestamp (datetime): ohlcv data are retrieved up to specified time inclusive.
                If the parameter is not specified then all data are retrieved
            limit (int): the number of ohlcv periods to retrieve

        Returns:
            DataFrame: ohlcv data

        Raises:
            GeneralAppException: No data was preliminarily uploaded for the specified timeframe.
            See the function upload_initial_ohlcv_data
        """
        if time_frame not in self._data:
            raise GeneralAppException(f"Timeframe {time_frame} does not exist")

        df = self._data[time_frame].data
        if to_timestamp:
            df = df.loc[:to_timestamp]
        if not limit or limit == len(df):
            return df
        return df.tail(limit)

