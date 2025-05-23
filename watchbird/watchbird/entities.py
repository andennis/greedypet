from typing_extensions import Self
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, Field, model_validator

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
    # PROFIT = "profit",
    # MULTI_TAKE = "multi-take"
    SIGNAL = "signal"


class ExchangeMode(Enum):
    SANDBOX = "sandbox"
    DEMO = "demo"
    REAL = "real"


class ExchangeConfig(BaseModel):
    id: ExchangeId
    api_key: str | None = None
    api_secret: str | None = None
    exchange_mode: ExchangeMode = ExchangeMode.SANDBOX
    max_retries_on_failure: int = 3
    max_retries_on_failure_delay: int = 500  # milliseconds


class ExchangeMarket(BaseModel):
    type: MarketType
    symbol: str


class StorageConfig(BaseModel):
    pass


class FilterCondition(BaseModel):
    operator: ConditionOperator
    # Field name from the Indicator's result structure
    name: str
    # Field value from the Indicator's result structure
    value: float | None = None


class FilterConfig(BaseModel):
    indicator: IndicatorType
    timeframe: TimeFrame
    condition: FilterCondition


class DealEntryConfig(BaseModel):
    filters: list[FilterConfig]


class ExitSignalConfig(BaseModel):
    filters: list[FilterConfig] = Field(default_factory=list)
    pnl: float | None = Field(ge=0, default=None)


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
    trade_algorithm: TradeAlgorithm
    entry_condition: DealEntryConfig
    exit_condition: DealExitConfig


class TradeSide(Enum):
    BUY = 1
    SELL = 2


@dataclass
class Trade:
    side: TradeSide
    price: float
    amount: float
    timestamp: int
