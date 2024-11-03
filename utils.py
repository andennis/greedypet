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


def get_closed_timeframes(timestamp: int) -> list[TimeFrame]:
    """
    The function returns all the timeframes closed at specified timestamp with permissible error at most 1 second.
    Args:
        timestamp (int): timestamp in seconds
    Return:
        list[TimeFrame]: list of timeframes corresponding to the specified timestamp
    """
    result = []
    for tf in TimeFrame:
        tf_size = timeframe_to_sec(tf)
        tf_ts = timestamp // tf_size * tf_size
        if timestamp - tf_ts < 1 or tf_ts + tf_size - timestamp < 1:
            result.append(tf)

    return result


def time_to_next_timeframe(timeframe: TimeFrame) -> int:
    """
    Calculate the number of seconds from current timestamp to the beginning of next timeframe
    for specified timeframe type (size).

    Args:
        timeframe (TimeFrame): the timeframe type
    Returns
        int:
    """
    tf = timeframe_to_sec(timeframe)
    cur_time = int(time.time())
    next_tf = cur_time // tf * tf + tf
    return next_tf - cur_time
