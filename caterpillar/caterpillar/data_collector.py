import asyncio
import logging
from datetime import datetime, timezone

from common.exchange.entities import ExchangeTrade
from common.exchange.entities import ExchangeTradeSide
from common.exchange.data_reader import ExchangeDataReader

from app_config import AppConfig
from dal.db_client import DbClient
from dal.models.currency_pair import CurrencyPair
from dal.repositories.currency_pair_repo import CurrencyPairRepository
from dal.repositories.trade_repo import TradeRepository
from dal.models.trade import Trade as DbTrade
from dal.models.trade import TradeSide as DbTradeSide

logger = logging.getLogger(__name__)


class DataCollector:
    def __init__(self, config: AppConfig):
        self._config = config
        self._data_reader = ExchangeDataReader(self._config.exchange)
        self._db_client = DbClient(
            self._config.database.connection, self._config.database.log_db_request
        )
        self._pairs: dict[str, CurrencyPair] = {}

    async def close(self):
        await self._db_client.close()
        await self._data_reader.close()

    async def _get_pairs(self) -> dict[str, CurrencyPair]:
        if not self._pairs:
            async with self._db_client.session() as session:
                repo = CurrencyPairRepository(session)
                pairs = await repo.get_active()
                self._pairs = {x.name: x for x in pairs}
        return self._pairs

    def _exchange_to_db_trade(self, trade: ExchangeTrade) -> DbTrade:
        return DbTrade(
            pair_id=self._pairs[trade.symbol].pair_id,
            price=trade.price,
            volume=trade.amount,
            side=(
                DbTradeSide.BUY
                if trade.side == ExchangeTradeSide.BUY
                else DbTradeSide.SELL
            ),
            timestamp=datetime.fromtimestamp(trade.timestamp / 1000, timezone.utc),
        )

    async def _write_to_db(self, trades: list[ExchangeTrade]):
        async with self._db_client.session() as session:
            repo = TradeRepository(session)
            for trade in trades:
                db_trade = self._exchange_to_db_trade(trade)
                repo.create(db_trade)
            await repo.commit()

    async def collecting_data(self):
        pairs = await self._get_pairs()
        symbols = list(pairs.keys())
        logger.info("Symbols to collect", extra=dict(symbols=symbols))
        try:
            while True:
                trades = await self._data_reader.read_latest_trades(symbols)
                await self._write_to_db(trades)
        except asyncio.CancelledError:
            logger.info("Trades reading finished")
        finally:
            await self._data_reader.close()
