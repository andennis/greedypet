from unittest.mock import patch
import pytest
from watchbird.entities import TimeFrame
from watchbird.utils import (
    timeframe_to_sec,
    get_closed_timeframes,
    get_time_to_next_timeframe,
    current_time_to_timeframe_time,
)


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
    "timestamp, delta, time_frames",
    [
        (0, 0, []),
        (1, 0, []),

        (60, 0, [TimeFrame.TF_1M]),
        (60, 0.1, [TimeFrame.TF_1M]),
        (60, 0.9, [TimeFrame.TF_1M]),
        (60, 1, []),

        (300, 0, [TimeFrame.TF_1M, TimeFrame.TF_5M]),
        (300, 0.5, [TimeFrame.TF_1M, TimeFrame.TF_5M]),
        (300, 1, [TimeFrame.TF_5M]),
        (300, 4, [TimeFrame.TF_5M]),
        (300, 5, []),

        (3600, 61, []),
        (3600, 60, [TimeFrame.TF_1M]),
        (3600, 59.5, [TimeFrame.TF_1M, TimeFrame.TF_1H]),
        (3600, 59, [TimeFrame.TF_1H]),
        (3600, 30, [TimeFrame.TF_1H]),
        (3600, 29, [TimeFrame.TF_30M, TimeFrame.TF_1H]),
        (3600, 15, [TimeFrame.TF_30M, TimeFrame.TF_1H]),
        (3600, 14, [TimeFrame.TF_15M, TimeFrame.TF_30M, TimeFrame.TF_1H]),
        (3600, 5, [TimeFrame.TF_15M, TimeFrame.TF_30M, TimeFrame.TF_1H]),
        (3600, 4, [TimeFrame.TF_5M, TimeFrame.TF_15M, TimeFrame.TF_30M, TimeFrame.TF_1H]),
        (3600, 3, [TimeFrame.TF_5M, TimeFrame.TF_15M, TimeFrame.TF_30M, TimeFrame.TF_1H]),
        (3600, 2, [TimeFrame.TF_3M, TimeFrame.TF_5M, TimeFrame.TF_15M, TimeFrame.TF_30M, TimeFrame.TF_1H]),
        (3600, 1, [TimeFrame.TF_3M, TimeFrame.TF_5M, TimeFrame.TF_15M, TimeFrame.TF_30M, TimeFrame.TF_1H]),
        (3600, 0, [TimeFrame.TF_1M, TimeFrame.TF_3M, TimeFrame.TF_5M, TimeFrame.TF_15M, TimeFrame.TF_30M, TimeFrame.TF_1H])
    ],
)
def test_get_closed_timeframes(timestamp: int, delta: float, time_frames: list[TimeFrame]):
    assert get_closed_timeframes(timestamp + delta) == time_frames
    if delta != 0:
        assert get_closed_timeframes(timestamp - delta) == time_frames


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
@patch("watchbird.utils.time.time")
def test_get_time_to_next_timeframe(
    mock_time,
    cur_time: int,
    time_frame: TimeFrame,
    result: int,
):
    mock_time.return_value = cur_time
    assert get_time_to_next_timeframe(time_frame) == result


@pytest.mark.parametrize(
    "cur_time, time_frame, result",
    [
        (600, TimeFrame.TF_5M, 600),
        (600.9, TimeFrame.TF_5M, 600),
        (599.1, TimeFrame.TF_5M, 600),
    ],
)
@patch("watchbird.utils.time.time")
def test_current_time_to_timeframe_time(
    mock_time,
    cur_time: int,
    time_frame: TimeFrame,
    result: int,
):
    mock_time.return_value = cur_time
    assert current_time_to_timeframe_time(time_frame) == result
