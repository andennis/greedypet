from .base_repo import BaseRepository
from ..models.currency_pair import CurrencyPair


class CurrencyPairRepository(BaseRepository[CurrencyPair]):
    model = CurrencyPair
    id_field = "pair_id"

    async def get_active(self) -> list[CurrencyPair]:
        return await self.get_list(is_active=True)

    async def add(self, base_currency: str, quote_currency: str) -> CurrencyPair:
        pair = self.model(base_currency=base_currency, quote_currency=quote_currency)
        return await self.create(pair)

    # @staticmethod
    # def to_dict(pair: CurrencyPair) -> Dict[str, Any]:
    #     return {
    #         "pair_id": pair.pair_id,
    #         "base_currency": pair.base_currency,
    #         "quote_currency": pair.quote_currency,
    #         "is_active": pair.is_active,
    #         "created_at": pair.created_at,
    #     }
