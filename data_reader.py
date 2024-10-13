import ccxt.pro as ccxt
from entities import TimeFrame, Exchange


class ExchangeDataReader:
    def __init__(self, exchange_config: Exchange):
        exchange_class = getattr(ccxt, exchange_config.name.value)
        self._exchange = exchange_class({
            'apiKey': exchange_config.api_key,
            'secret': exchange_config.api_secret,
        })
        self._exchange.set_sandbox_mode(exchange_config.test_mode)

    @property
    def exchange(self):
        return self._exchange

    async def read_initial_data(self, symbol: str, time_frame: TimeFrame, limit: int) -> list[list[float]]:
        return await self._exchange.fetch_mark_ohlcv(symbol, timeframe=time_frame.value, limit=limit)

    async def read_latest_trades(self, symbol: str):
        pass
