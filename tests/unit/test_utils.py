from unittest.mock import patch
import pytest
from datetime import datetime
from entities import TimeFrame
from utils import timeframe_to_sec, get_closed_timeframes, time_to_next_timeframe


@pytest.mark.parametrize(
    "time_frame, seconds",
    [
        (TimeFrame.TF_1M, 60),
        (TimeFrame.TF_3M, 60 * 3),
        (TimeFrame.TF_5M, 60 * 5),
        (TimeFrame.TF_15M, 60 * 15),
        (TimeFrame.TF_30M, 60 * 30),
        (TimeFrame.TF_1H, 60 * 60),
        (TimeFrame.TF_2H, 2 * 60 * 60),
        (TimeFrame.TF_4H, 4 * 60 * 60),
        (TimeFrame.TF_6H, 6 * 60 * 60),
        (TimeFrame.TF_12H, 12 * 60 * 60),
        (TimeFrame.TF_1D, 24 * 60 * 60),
        (TimeFrame.TF_1W, 7 * 24 * 60 * 60),
    ],
)
def test_timeframe_to_sec(time_frame: TimeFrame, seconds: int):
    assert timeframe_to_sec(time_frame) == seconds


@pytest.mark.parametrize(
    "timestamp, time_frames",
    [
        (660, {TimeFrame.TF_1M}),
        (660.7, {TimeFrame.TF_1M}),
        (659.3, {TimeFrame.TF_1M}),
        (661, set()),
        (600, {TimeFrame.TF_1M, TimeFrame.TF_5M}),
        (900, {TimeFrame.TF_1M, TimeFrame.TF_3M, TimeFrame.TF_5M, TimeFrame.TF_15M}),
        (
            3600,
            {
                TimeFrame.TF_1M,
                TimeFrame.TF_3M,
                TimeFrame.TF_5M,
                TimeFrame.TF_15M,
                TimeFrame.TF_30M,
                TimeFrame.TF_1H,
            },
        ),
        (
            datetime(2024, 11, 2, 5, 45).timestamp(),
            {TimeFrame.TF_1M, TimeFrame.TF_3M, TimeFrame.TF_5M, TimeFrame.TF_15M},
        ),
    ],
)
def test_get_closed_timeframes(timestamp: int, time_frames: list[TimeFrame]):
    result = get_closed_timeframes(timestamp)
    assert set(result) == time_frames


@pytest.mark.parametrize(
    "cur_time, time_frame, result",
    [
        (600, TimeFrame.TF_1M, 60),
        (601, TimeFrame.TF_1M, 59),
        (659, TimeFrame.TF_1M, 1),
        (600, TimeFrame.TF_5M, 5 * 60),
        (600 + 150, TimeFrame.TF_5M, 5 * 60 - 150),
        (3600, TimeFrame.TF_15M, 15 * 60),
        (3600 + 600, TimeFrame.TF_15M, 15 * 60 - 600),
    ],
)
@patch("market_data_analyzer.time.time")
def test_sleep_to_next_timeframe(
    mock_time,
    cur_time: int,
    time_frame: TimeFrame,
    result: int,
):
    mock_time.return_value = cur_time
    assert time_to_next_timeframe(time_frame) == result
