from .base_repo import BaseRepository
from ..models.currency_pair import CurrencyPair


class CurrencyPairRepository(BaseRepository[CurrencyPair]):
    model = CurrencyPair
    id_field = "pair_id"

    async def get_active(self) -> list[CurrencyPair]:
        return await self.get_list(is_active=True)

    def add(self, symbol: str) -> CurrencyPair:
        return self.create(CurrencyPair(name=symbol))
