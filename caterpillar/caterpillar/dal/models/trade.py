from enum import Enum
from datetime import datetime
from decimal import Decimal
from typing_extensions import Annotated

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, ForeignKey, TIMESTAMP, Numeric
from sqlalchemy import Enum as SQLEnum

from .base_model import Base, pk_int

numeric20_8 = Annotated[Decimal, mapped_column(Numeric(20, 8), nullable=False)]


class TradeSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class Trade(Base):
    __tablename__ = "trades"

    pair_id: Mapped[int] = mapped_column(Integer, ForeignKey("currency_pairs.pair_id"), primary_key=True)
    price: Mapped[numeric20_8]
    volume: Mapped[numeric20_8]
    side: Mapped[TradeSide] = mapped_column(SQLEnum(TradeSide), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), primary_key=True)
