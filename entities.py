from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self
from enum import Enum
from dataclasses import dataclass

OhlcvData = list[list[float]]


class ExchangeId(Enum):
    BYBIT = "bybit"


class MarketType(Enum):
    SPOT = "spot"


class TradeAlgorithm(Enum):
    LONG = "long"
    SHORT = "short"


class IndicatorType(Enum):
    BOLLINGER_BENDS = "BB"
    RSI = "RSI"


class TimeFrame(Enum):
    TF_1M = "1m"
    TF_3M = "3m"
    TF_5M = "5m"
    TF_15M = "15m"
    TF_30M = "30m"
    TF_1H = "1h"
    TF_2H = "2h"
    TF_4H = "4h"
    TF_6H = "6h"
    TF_12H = "12h"
    TF_1D = "1d"
    TF_1W = "1w"


class ConditionOperator(Enum):
    GT = "gt"
    LT = "lt"


class ExitMode(Enum):
    PROFIT = "profit",
    MULTI_TAKE = "multi-take"
    SIGNAL = "signal"


class TradingMode(Enum):
    SANDBOX = "sandbox"
    DEMO = "demo"
    REAL = "real"


class Exchange(BaseModel):
    id: ExchangeId
    api_key: str | None = None
    api_secret: str | None = None
    trading_mode: TradingMode | None = TradingMode.SANDBOX


class ExchangeMarket(BaseModel):
    type: MarketType = MarketType.SPOT
    symbol: str


class StorageConfig(BaseModel):
    pass


class FilterCondition(BaseModel):
    operator: ConditionOperator
    value: float


class MovingAverageType(Enum):
    SMA = "sma"
    EMA = "ema"


class FilterConfig(BaseModel):
    indicator: IndicatorType
    time_frame: TimeFrame
    # periods: int | None = Field(gt=0, default=None)
    # moving_average: MovingAverageType | None = None
    condition: FilterCondition | None = None


class DealEntryConfig(BaseModel):
    filters: list[FilterConfig]


class ExitSignalConfig(BaseModel):
    filters: list[FilterConfig] = []
    pnl: float | None = Field(ge=-100, le=100, default=None)


class DealExitConfig(BaseModel):
    mode: ExitMode
    signal: ExitSignalConfig | None = None

    @model_validator(mode='after')
    def signa_validator(self) -> Self:
        if self.mode == ExitMode.SIGNAL:
            if self.signal is None:
                raise ValueError(f"The field <signal> must be set for the mode {self.mode}")
        return self


class DealConfig(BaseModel):
    trade_algorithm: TradeAlgorithm = TradeAlgorithm.LONG
    entry_condition: DealEntryConfig
    exit_condition: DealExitConfig


class DealState(Enum):
    LOOK_FOR_ENTRY_POINT = 1
    IN_DEAL = 2


class DealEntryCondition(BaseModel):
    pass


class DealExitCondition(BaseModel):
    pass


class Deal(BaseModel):
    algorithm: TradeAlgorithm
    state: DealState = DealState.LOOK_FOR_ENTRY_POINT
    deal_average_price: float | None = None
    entry_condition: DealEntryCondition
    exit_condition: DealExitCondition


class TradeSide(Enum):
    BUY = 1
    SELL = 2


@dataclass
class Trade:
    side: TradeSide
    price: float
    amount: float
    timestamp: int
