import pytest
from entities import TimeFrame
from utils import timeframe_to_sec


@pytest.mark.parametrize("time_frame, seconds", [
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
    (TimeFrame.TF_1W, 7 * 24 * 60 * 60)
])
def test_timeframe_to_sec(time_frame: TimeFrame, seconds: int):
    assert timeframe_to_sec(time_frame) == seconds
