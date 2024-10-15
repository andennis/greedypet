from pydantic import BaseModel, Field
from enum import Enum, IntEnum
from dataclasses import dataclass


class ExchangeId(str, Enum):
    BYBIT = "bybit"


class MarketType(str, Enum):
    SPOT = "spot"


class TradeAlgorithm(str, Enum):
    LONG = ("long",)
    SHORT = "short"


class FilterType(str, Enum):
    BOLLINGER_BENDS = "BB"
    RSI = "RSI"


class TimeFrame(str, Enum):
    TF_1M = "1m"
    TF_5M = "5m"
    TF_15M = "15m"
    TF_30M = "30m"
    TF_1H = "1h"
    TF_1D = "1d"
    TF_1W = "1w"


class ConditionOperator(str, Enum):
    GT = "gt"
    LT = "lt"


class ExitMode(str, Enum):
    SIGNAL = "signal"


class Exchange(BaseModel):
    id: ExchangeId
    api_key: str | None = None
    api_secret: str | None = None
    test_mode: bool | None = True
    # demo_trading: bool | None = False


class ExchangeMarket(BaseModel):
    type: MarketType
    symbol: str


class FilterCondition(BaseModel):
    operator: ConditionOperator
    value: float


class Filter(BaseModel):
    type: FilterType
    time_frame: TimeFrame
    condition: FilterCondition | None = None


class EntryCondition(BaseModel):
    filters: list[Filter]


class ExitSignal(BaseModel):
    filters: list[Filter]
    pnl: float = Field(ge=-100, le=100)


class ExitCondition(BaseModel):
    mode: ExitMode
    signal: ExitSignal


class TradeSide(IntEnum):
    BUY = 1
    SELL = 2


@dataclass
class Trade:
    side: TradeSide
    price: float
    amount: float
    timestamp: int
