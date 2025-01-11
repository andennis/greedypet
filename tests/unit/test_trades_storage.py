import pytest
import numpy
import pandas as pd
from datetime import timedelta, datetime
from exceptions import GeneralAppException
from trades_storage import TradesStorage
from entities import TimeFrame, Trade, TradeSide


DT_FORMAT = "%Y-%m-%dT%H:%M:%S"
OHLCV_DATA_30M = [
    # timestamp     open     high     low       close     volume
    [1729535400000, 67012.8, 67012.8, 66686.93, 66999.28, 0.061758],  # 2024-10-21 18:30
    [1729537200000, 66999.28, 67012.8, 66700.0, 67012.8, 0.048467],
    [1729539000000, 67012.8, 67012.8, 67012.8, 67012.8, 0.060964],
    [1729540800000, 67012.8, 67012.8, 67012.8, 67012.8, 0.078364],
    [1729542600000, 67012.8, 67013, 66912, 67000, 0.003],  # 2024-10-21 20:30
]


def test_upload_initial_ohlcv_data(trades_storage: TradesStorage):
    df = trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, OHLCV_DATA_30M)
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


@pytest.mark.parametrize(
    "to_timestamp, limit, periods, last_row",
    [
        (None, None, len(OHLCV_DATA_30M), 4),
        (None, len(OHLCV_DATA_30M) + 1, len(OHLCV_DATA_30M), 4),
        (None, 1, 1, 4),
        (OHLCV_DATA_30M[4][0], None, len(OHLCV_DATA_30M), 4),
        (OHLCV_DATA_30M[4][0] + 1000, None, len(OHLCV_DATA_30M), 4),
        (OHLCV_DATA_30M[4][0] - 1000, None, len(OHLCV_DATA_30M) - 1, 3),
        (OHLCV_DATA_30M[3][0], None, len(OHLCV_DATA_30M) - 1, 3),
        (OHLCV_DATA_30M[3][0], 1, 1, 3),
    ],
)
def test_get_latest_periods(
    trades_storage: TradesStorage,
    to_timestamp: int,
    limit: int,
    periods: int,
    last_row: int,
):
    trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, OHLCV_DATA_30M)
    df = trades_storage.get_latest_periods(
        TimeFrame.TF_30M,
        to_timestamp=pd.Timestamp(to_timestamp, unit="ms") if to_timestamp else None,
        limit=limit,
    )
    assert df is not None
    assert len(df) == periods
    assert df.index[-1] == pd.Timestamp(OHLCV_DATA_30M[last_row][0], unit="ms")


def test_get_latest_periods_failed(trades_storage: TradesStorage):
    with pytest.raises(GeneralAppException):
        trades_storage.get_latest_periods(TimeFrame.TF_5M, datetime.now())

    trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, OHLCV_DATA_30M)
    with pytest.raises(GeneralAppException):
        trades_storage.get_latest_periods(TimeFrame.TF_5M, datetime.now())


@pytest.mark.parametrize(
    "new_price, param_changed", [(67012, ""), (67013, "high"), (66912, "low")]
)
def test_add_trade_into_latest_timeframe(
    new_price: float, param_changed: str, trades_storage: TradesStorage
):
    data = trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, OHLCV_DATA_30M)
    # [1729542600000, 67012.8, 67012.8, 66912.28, 67012.8, 0.003]
    saved_tf = trades_storage.get_latest_periods(TimeFrame.TF_30M, limit=1).copy()

    trade = Trade(
        side=TradeSide.BUY,
        price=new_price,
        amount=0.01,
        timestamp=(data.index[-1].timestamp() + timedelta(minutes=1).total_seconds())
        * 1000,
    )
    trades_storage.add_trade(trade)
    last_tf = trades_storage.get_latest_periods(TimeFrame.TF_30M, limit=1)

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


def test_add_trades_into_latest_timeframe(trades_storage: TradesStorage):
    data = trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, OHLCV_DATA_30M)
    # [1729542600000, 67012.8, 67012.8, 66912.28, 67012.8, 0.003]
    saved_tf = trades_storage.get_latest_periods(TimeFrame.TF_30M, limit=1).copy()

    latest_ts = data.index[-1].timestamp() * 1000
    for price in [67000, 68000, 66000, 66100, 66101]:
        latest_ts += timedelta(minutes=1).total_seconds() * 1000
        trade = Trade(side=TradeSide.BUY, price=price, amount=0.01, timestamp=latest_ts)
        trades_storage.add_trade(trade)

    last_tf = trades_storage.get_latest_periods(TimeFrame.TF_30M, limit=1)

    stf = saved_tf.iloc[-1]
    ltf = last_tf.iloc[-1]
    assert ltf.open == stf.open
    assert ltf.high == 68000
    assert ltf.low == 66000
    assert ltf.close == 66101
    assert ltf.volume == stf.volume + 0.01 * 5


def test_add_trade_into_new_timeframe(trades_storage: TradesStorage):
    data = trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, OHLCV_DATA_30M)
    saved_tf = trades_storage.get_latest_periods(TimeFrame.TF_30M, limit=1).copy()

    latest_ts = (
        data.index[-1].timestamp() + timedelta(minutes=31).total_seconds()
    ) * 1000
    trade = Trade(side=TradeSide.BUY, price=6700, amount=0.01, timestamp=latest_ts)
    trades_storage.add_trade(trade)

    last_tf = trades_storage.get_latest_periods(TimeFrame.TF_30M, limit=1)
    stf = saved_tf.iloc[-1]
    ltf = last_tf.iloc[-1]
    assert ltf.open == stf.close
    assert ltf.high == trade.price
    assert ltf.low == trade.price
    assert ltf.close == trade.price
    assert ltf.volume == trade.amount


def test_add_trades_into_old_timeframe(trades_storage: TradesStorage):
    data = trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, OHLCV_DATA_30M)
    latest_ts = (
        data.index[-1].timestamp() - timedelta(minutes=1).total_seconds()
    ) * 1000
    trade = Trade(side=TradeSide.BUY, price=6700, amount=0.01, timestamp=latest_ts)
    with pytest.raises(GeneralAppException):
        trades_storage.add_trade(trade)


@pytest.mark.parametrize(
    "init_time_shift, time_shift, price, expected_high, expected_low, expected_close",
    [
        (0, 0, 67010, 67013, 66912, 67000),  # existing timestamp - close not updated
        (
            1,
            1,
            67010,
            67013,
            66912,
            67000,
        ),  # next existing timestamp - close not updated
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
):
    # GIVEN The latest trade
    # [1729542600000, 67012.8, 67013, 66912, 67000, 0.003]
    data = trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, OHLCV_DATA_30M)
    if init_time_shift > 0:
        trade = Trade(
            side=TradeSide.BUY,
            price=OHLCV_DATA_30M[-1][4],
            amount=0.01,
            timestamp=(
                data.index[-1].timestamp()
                + timedelta(minutes=init_time_shift).total_seconds()
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
            data.index[-1].timestamp() + timedelta(minutes=time_shift).total_seconds()
        )
        * 1000,
    )
    trades_storage.add_trade(trade)

    # THEN
    last_tf = trades_storage.get_latest_periods(TimeFrame.TF_30M, limit=1)
    ltf = last_tf.iloc[-1]
    assert ltf.high == expected_high
    assert ltf.low == expected_low
    assert ltf.close == expected_close


def test_get_close_price(trades_storage: TradesStorage):
    trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, OHLCV_DATA_30M)
    latest_ts = pd.Timestamp(OHLCV_DATA_30M[4][0], unit="ms")
    result = trades_storage.get_close_price(TimeFrame.TF_30M, latest_ts)
    assert result == OHLCV_DATA_30M[4][4]


def test_get_close_price_failed(trades_storage: TradesStorage):
    trades_storage.upload_initial_ohlcv_data(TimeFrame.TF_30M, OHLCV_DATA_30M)
    with pytest.raises(GeneralAppException) as e:
        trades_storage.get_close_price(TimeFrame.TF_5M, datetime.now())
    assert "Timeframe" in e.value.args[0]

    with pytest.raises(GeneralAppException) as e:
        trades_storage.get_close_price(TimeFrame.TF_30M, datetime.now())
    assert "Timestamp" in e.value.args[0]
