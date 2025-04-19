
from datetime import datetime
from decimal import Decimal
from typing_extensions import Annotated

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import TIMESTAMP, Integer, ForeignKey, Numeric

from .base_model import Base

numeric20_8 = Annotated[Decimal, mapped_column(Numeric(20, 8), nullable=False)]


class OHLCVData(Base):
    __tablename__ = "trades_1min_ohlcv"

    bucket: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), primary_key=True)
    pair_id: Mapped[int] = mapped_column(Integer, ForeignKey("currency_pairs.pair_id"), primary_key=True)
    # prices
    open: Mapped[numeric20_8]
    high: Mapped[numeric20_8]
    low: Mapped[numeric20_8]
    close: Mapped[numeric20_8]
    # trade volumes
    buy_volume: Mapped[numeric20_8]
    sell_volume: Mapped[numeric20_8]
    # number of traders
    buy_trades: Mapped[int] = mapped_column(Integer, nullable=False)
    sell_trades: Mapped[int] = mapped_column(Integer, nullable=False)


