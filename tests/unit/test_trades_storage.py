import pytest
import numpy
import pandas as pd
import datetime
from exceptions import GeneralAppException
from trades_storage import TradesStorage
from entities import StorageConfig, TimeFrame, Trade, TradeSide


@pytest.fixture
def ohlcv_data_30m():
    return [
        [1729535400000, 67012.8, 67012.8, 66686.93, 66999.28, 0.061758],
        [1729537200000, 66999.28, 67012.8, 66700.0, 67012.8, 0.048467],
        [1729539000000, 67012.8, 67012.8, 67012.8, 67012.8, 0.060964],
        [1729540800000, 67012.8, 67012.8, 67012.8, 67012.8, 0.078364],
        [1729542600000, 67012.8, 67013, 66912, 67000, 0.003],
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


@pytest.mark.parametrize("data", [None, [], [[]], [[1, 2, 3]]])
def test_upload_initial_ohlcv_data_wrong_data(trades_storage: TradesStorage, data):
    with pytest.raises(GeneralAppException):
        trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, data)


def test_get_latest_timeframes(trades_storage: TradesStorage, ohlcv_data_30m):
    trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, ohlcv_data_30m)
    df = trades_storage.get_latest_timeframes(TimeFrame.TF_30M, 1)
    assert df is not None
    assert len(df) == 1
    assert df.iloc[0].values.flatten().tolist() == ohlcv_data_30m[4][1:]
    assert df.index[0] == pd.Timestamp(ohlcv_data_30m[4][0], unit="ms")


def test_get_latest_timeframes_failed(trades_storage: TradesStorage, ohlcv_data_30m):
    with pytest.raises(GeneralAppException):
        trades_storage.get_latest_timeframes(TimeFrame.TF_5M, 1)

    trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, ohlcv_data_30m)
    with pytest.raises(GeneralAppException):
        trades_storage.get_latest_timeframes(TimeFrame.TF_5M, 1)


@pytest.mark.parametrize(
    "new_price, param_changed", [(67012, ""), (67013, "high"), (66912, "low")]
)
def test_add_trade_into_latest_timeframe(
    new_price: float, param_changed: str, trades_storage: TradesStorage, ohlcv_data_30m
):
    data = trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, ohlcv_data_30m)
    # [1729542600000, 67012.8, 67012.8, 66912.28, 67012.8, 0.003]
    saved_tf = trades_storage.get_latest_timeframes(TimeFrame.TF_30M, limit=1).copy()

    trade = Trade(
        side=TradeSide.BUY,
        price=new_price,
        amount=0.01,
        timestamp=(
            data.index[-1].timestamp() + datetime.timedelta(minutes=1).total_seconds()
        )
        * 1000,
    )
    trades_storage.add_trade(trade)
    last_tf = trades_storage.get_latest_timeframes(TimeFrame.TF_30M, limit=1)

    stf = saved_tf.iloc[-1]
    ltf = last_tf.iloc[-1]
    assert ltf.open == stf.open
    for prm in ["high", "low"]:
        if prm == param_changed:
            assert ltf[prm] == trade.price
        else:
            assert ltf[prm] == stf[prm]
    assert ltf.close == trade.price
    assert ltf.volume == stf.volume + trade.amount


def test_add_trades_into_latest_timeframe(
    trades_storage: TradesStorage, ohlcv_data_30m
):
    data = trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, ohlcv_data_30m)
    # [1729542600000, 67012.8, 67012.8, 66912.28, 67012.8, 0.003]
    saved_tf = trades_storage.get_latest_timeframes(TimeFrame.TF_30M, limit=1).copy()

    latest_ts = data.index[-1].timestamp() * 1000
    for price in [67000, 68000, 66000, 66100, 66101]:
        latest_ts += datetime.timedelta(minutes=1).total_seconds() * 1000
        trade = Trade(side=TradeSide.BUY, price=price, amount=0.01, timestamp=latest_ts)
        trades_storage.add_trade(trade)

    last_tf = trades_storage.get_latest_timeframes(TimeFrame.TF_30M, limit=1)

    stf = saved_tf.iloc[-1]
    ltf = last_tf.iloc[-1]
    assert ltf.open == stf.open
    assert ltf.high == 68000
    assert ltf.low == 66000
    assert ltf.close == 66101
    assert ltf.volume == stf.volume + 0.01 * 5


def test_add_trade_into_new_timeframe(trades_storage: TradesStorage, ohlcv_data_30m):
    data = trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, ohlcv_data_30m)
    saved_tf = trades_storage.get_latest_timeframes(TimeFrame.TF_30M, limit=1).copy()

    latest_ts = (
        data.index[-1].timestamp() + datetime.timedelta(minutes=31).total_seconds()
    ) * 1000
    trade = Trade(side=TradeSide.BUY, price=6700, amount=0.01, timestamp=latest_ts)
    trades_storage.add_trade(trade)

    last_tf = trades_storage.get_latest_timeframes(TimeFrame.TF_30M, limit=1)
    stf = saved_tf.iloc[-1]
    ltf = last_tf.iloc[-1]
    assert ltf.open == stf.close
    assert ltf.high == trade.price
    assert ltf.low == trade.price
    assert ltf.close == trade.price
    assert ltf.volume == trade.amount


def test_add_trades_into_old_timeframe(trades_storage: TradesStorage, ohlcv_data_30m):
    data = trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, ohlcv_data_30m)
    latest_ts = (
        data.index[-1].timestamp() - datetime.timedelta(minutes=1).total_seconds()
    ) * 1000
    trade = Trade(side=TradeSide.BUY, price=6700, amount=0.01, timestamp=latest_ts)
    with pytest.raises(GeneralAppException):
        trades_storage.add_trade(trade)


@pytest.mark.parametrize(
    "init_time_shift, time_shift, price, expected_high, expected_low, expected_close",
    [
        (0, 0, 67010, 67013, 66912, 67000),  # existing timestamp - close not updated
        (1, 1, 67010, 67013, 66912, 67000),  # next existing timestamp - close not updated
        (0, 0, 67014, 67014, 66912, 67000),  # existing timestamp only high updated
        (0, 0, 66900, 67013, 66900, 67000),  # existing timestamp only low updated
        (0, 1, 67010, 67013, 66912, 67010),  # next timestamp - close updated
        (0, 1, 67014, 67014, 66912, 67014),  # next timestamp - high and close updated
        (0, 1, 66900, 67013, 66900, 66900),  # next timestamp - low and close updated
    ],
)
def test_add_trade_with_earlier_timestamp(
    init_time_shift,
    time_shift,
    price,
    expected_high,
    expected_low,
    expected_close,
    trades_storage: TradesStorage,
    ohlcv_data_30m,
):
    # GIVEN The latest trade
    # [1729542600000, 67012.8, 67013, 66912, 67000, 0.003]
    data = trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, ohlcv_data_30m)
    if init_time_shift > 0:
        trade = Trade(
            side=TradeSide.BUY,
            price=ohlcv_data_30m[-1][4],
            amount=0.01,
            timestamp=(
                data.index[-1].timestamp()
                + datetime.timedelta(minutes=init_time_shift).total_seconds()
            )
            * 1000,
        )
        trades_storage.add_trade(trade)

    # WHEN
    trade = Trade(
        side=TradeSide.BUY,
        price=price,
        amount=0.01,
        timestamp=(
            data.index[-1].timestamp()
            + datetime.timedelta(minutes=time_shift).total_seconds()
        )
        * 1000,
    )
    trades_storage.add_trade(trade)

    # THEN
    last_tf = trades_storage.get_latest_timeframes(TimeFrame.TF_30M, limit=1)
    ltf = last_tf.iloc[-1]
    assert ltf.high == expected_high
    assert ltf.low == expected_low
    assert ltf.close == expected_close
