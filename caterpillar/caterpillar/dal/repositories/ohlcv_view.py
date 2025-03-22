from datetime import datetime
from sqlalchemy import select

from ..models.olhcv_data import OHLCVData
from .base_view import BaseViewRepository


class OHLCVViewRepository(BaseViewRepository[OHLCVData]):
    model = OHLCVData

    async def get_candles(
        self, pair_id: int, start_time: datetime, end_time: datetime
    ) -> list[OHLCVData]:
        query = (
            select(OHLCVData)
            .where(OHLCVData.pair_id == pair_id)
            .where(OHLCVData.bucket.between(start_time, end_time))
            .order_by(OHLCVData.bucket)
        )
        return await self.execute_query(query)

    # @staticmethod
    # def to_dict(candle: OHLCVData) -> Dict[str, Any]:
    #     return {
    #         "timestamp": candle.bucket,
    #         "open": float(candle.open),
    #         "high": float(candle.high),
    #         "low": float(candle.low),
    #         "close": float(candle.close),
    #         "volume": float(candle.volume),
    #         "number_of_trades": candle.number_of_trades,
    #     }
