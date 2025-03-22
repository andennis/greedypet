from typing import Any
from datetime import datetime

from sqlalchemy import select

from .base_repo import BaseRepository
from ..models.trade import Trade


class TradeRepository(BaseRepository[Trade]):
    model = Trade

    async def get_filtered(
        self,
        pair_id: int | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 1000,
    ) -> list[Trade]:
        query = select(Trade).order_by(Trade.timestamp.desc()).limit(limit)

        if pair_id is not None:
            query = query.where(Trade.pair_id == pair_id)
        if start_time is not None:
            query = query.where(Trade.timestamp >= start_time)
        if end_time is not None:
            query = query.where(Trade.timestamp <= end_time)

        return await self.execute_query(query)

    # @staticmethod
    # def to_dict(trade: Trade) -> dict[str, Any]:
    #     """
    #     Convert Trade instance to dictionary.
    #
    #     Args:
    #         trade: Trade instance
    #
    #     Returns:
    #         Dictionary with trade data
    #     """
    #     return {
    #         "pair_id": trade.pair_id,
    #         "price": float(trade.price),
    #         "volume": float(trade.volume),
    #         "side": trade.side.value,
    #         "timestamp": trade.timestamp,
    #     }
