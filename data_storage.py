from entities import TimeFrame, TradeSide


class GPDataStorage:
    def __init__(self, symbol: str):
        self._symbol = symbol

    def save_trade(self, timestamp: int, side: TradeSide, price: float, volume: float):
        pass

    def get_ohlcv(self, time_frame: TimeFrame, limit: int) -> list[list[float]]:
        return []
