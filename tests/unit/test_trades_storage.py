import pytest
import numpy
import pandas as pd
from datetime import datetime
from trades_storage import TradesStorage
from entities import StorageConfig, TimeFrame


@pytest.fixture
def symbol():
    return "BTC/USDT"


@pytest.fixture
def trades_storage(symbol: str):
    return TradesStorage(StorageConfig(), symbol)


@pytest.fixture
def ohlcv_data_30m():
    return [
        [1729535400000, 67012.8, 67012.8, 66686.93, 66999.28, 0.061758],
        [1729537200000, 66999.28, 67012.8, 66700.0, 67012.8, 0.048467],
        [1729539000000, 67012.8, 67012.8, 67012.8, 67012.8, 0.060964],
        [1729540800000, 67012.8, 67012.8, 67012.8, 67012.8, 0.078364],
        [1729542600000, 67012.8, 67012.8, 66912.28, 67012.8, 0.003286]
    ]


def test_upload_initial_ohlcv_data(trades_storage: TradesStorage, ohlcv_data_30m):
    df = trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, ohlcv_data_30m)
    assert df is not None
    assert len(df) == 5
    assert df.index.name == "timestamp"
    assert df.index.dtype.type == numpy.datetime64
    assert len(df.columns) == 5
    assert df.columns[0] == "open"
    assert df.columns[1] == "high"
    assert df.columns[2] == "low"
    assert df.columns[3] == "close"
    assert df.columns[4] == "volume"
    assert df["open"].dtype == numpy.float64
    assert df["high"].dtype == numpy.float64
    assert df["low"].dtype == numpy.float64
    assert df["close"].dtype == numpy.float64
    assert df["volume"].dtype == numpy.float64


def test_get_latest_ohlcv_data(trades_storage: TradesStorage, ohlcv_data_30m):
    trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, ohlcv_data_30m)
    df = trades_storage.get_latest_ohlcv_data(TimeFrame.TF_30M, 1)
    assert df is not None
    assert len(df) == 1
    assert df.iloc[0].values.flatten().tolist() == ohlcv_data_30m[4][1:]
    assert df.index[0] == pd.Timestamp(ohlcv_data_30m[4][0], unit="ms")
