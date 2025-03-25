from datetime import datetime
from typing_extensions import Annotated

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Boolean, TIMESTAMP, func

from .base_model import Base, pk_int

str10 = Annotated[str, mapped_column(String(10), nullable=False)]


class CurrencyPair(Base):
    __tablename__ = "currency_pairs"

    pair_id: Mapped[pk_int]
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
