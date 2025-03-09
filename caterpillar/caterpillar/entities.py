from enum import Enum
from pydantic import BaseModel


class ExchangeId(Enum):
    BYBIT = "bybit"


class MarketType(Enum):
    SPOT = "spot"


class ExchangeMarket(BaseModel):
    type: MarketType
    symbols: list[str]


class ExchangeConfig(BaseModel):
    id: ExchangeId
    api_key: str | None = None
    api_secret: str | None = None
    max_retries_on_failure: int = 3
    max_retries_on_failure_delay: int = 500  # milliseconds
