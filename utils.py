import time
from entities import TimeFrame
from exceptions import NotSupported


# class Singleton(type):
#     _instances = {}
#
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]


def timeframe_to_sec(time_frame: TimeFrame) -> int:
    amount = int(time_frame.value[0:-1])
    unit = time_frame.value[-1]
    match unit:
        case "w":
            scale = 60 * 60 * 24 * 7
        case "d":
            scale = 60 * 60 * 24
        case "h":
            scale = 60 * 60
        case "m":
            scale = 60
        case _:
            raise NotSupported(f"Time frame unit {unit} is not supported")

    return amount * scale


def get_closed_timeframes(timestamp: float) -> list[TimeFrame]:
    """
    The function returns all the timeframes closed at specified timestamp with permissible error
    at most 1/60 of timeframe size.

    Args:
        timestamp (float): timestamp in seconds
    Return:
        list[TimeFrame]: list of timeframes corresponding to the specified timestamp
    """
    result = []
    for tf in TimeFrame:
        tf_size = timeframe_to_sec(tf)
        d = tf_size // 60
        if timestamp > d:
            tf_ts = timestamp // tf_size * tf_size
            if timestamp - tf_ts < d or tf_ts + tf_size - timestamp < d:
                result.append(tf)

    return result


def get_time_to_next_timeframe(timeframe: TimeFrame) -> int:
    """
    Calculate the number of seconds from current timestamp to the beginning of next timeframe
    for specified timeframe type (size).

    Args:
        timeframe (TimeFrame): the timeframe type
    Returns
        int: number of seconds to the beginning of next timeframe period
    """
    tf = timeframe_to_sec(timeframe)
    cur_time = int(time.time())
    next_tf = cur_time // tf * tf + tf
    return next_tf - cur_time


def current_time_to_timeframe_time(timeframe: TimeFrame) -> int:
    """
    Adjust the current time to the open time of nearest timeframe

    Args:
        timeframe (TimeFrame): the timeframe type
    Returns:
        int: open timestamp (in seconds) of the nearest timeframe period
    """
    tf = timeframe_to_sec(timeframe)
    cur_time = int(time.time())
    tf_ts = cur_time // tf * tf
    return tf_ts + (tf if cur_time - tf_ts > 1 else 0)
