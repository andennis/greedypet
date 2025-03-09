from enum import Enum

from pydantic import BaseModel


class DealPhase(Enum):
    LOOK_FOR_ENTRY_POINT = 1
    IN_DEAL = 2


class DealState(BaseModel):
    phase: DealPhase = DealPhase.LOOK_FOR_ENTRY_POINT
    average_price: float | None = None
