from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

OhlcvData = list[list[float]]


class ExchangeId(Enum):
    BYBIT = "bybit"


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


class ExchangeMode(Enum):
    SANDBOX = "sandbox"
    DEMO = "demo"
    REAL = "real"


class ExchangeConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GRPT_EXCHANGE_", env_ignore_empty=True, extra="ignore"
    )

    id: ExchangeId = ExchangeId.BYBIT
    api_key: str | None = None
    api_secret: str | None = None
    mode: ExchangeMode = ExchangeMode.REAL
    max_retries_on_failure: int = 3
    max_retries_on_failure_delay: int = 500  # milliseconds


class ExchangeTradeSide(Enum):
    BUY = 1
    SELL = 2


@dataclass
class ExchangeTrade:
    symbol: str
    side: ExchangeTradeSide
    price: float
    amount: float
    timestamp: int
