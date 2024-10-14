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
    if "w" == unit:
        scale = 60 * 60 * 24 * 7
    elif "d" == unit:
        scale = 60 * 60 * 24
    elif "h" == unit:
        scale = 60 * 60
    elif "m" == unit:
        scale = 60
    else:
        raise NotSupported(f"Time frame unit {unit} is not supported")

    return amount * scale
