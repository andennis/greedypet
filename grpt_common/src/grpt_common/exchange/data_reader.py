import ccxt.pro as ccxt

from grpt_common.exchange.entities import (
    TimeFrame,
    ExchangeConfig,
    ExchangeTrade,
    ExchangeTradeSide,
    ExchangeMode,
    OhlcvData,
)


class ExchangeDataReader:
    """
    The exchange data reader reads data from the exchange
    """

    def __init__(self, exchange_config: ExchangeConfig):
        exchange_class = getattr(ccxt, exchange_config.id.value)
        self._exchange = exchange_class(
            {
                # "apiKey": os.environ.get("GP_API_KEY", exchange_config.api_key),
                # "secret": os.environ.get("GP_API_SECRET", exchange_config.api_secret),
                "options": {
                    "maxRetriesOnFailure": exchange_config.max_retries_on_failure,
                    "maxRetriesOnFailureDelay": exchange_config.max_retries_on_failure_delay,
                },
            }
        )
        if exchange_config.mode == ExchangeMode.SANDBOX:
            self._exchange.set_sandbox_mode(True)
        elif exchange_config.mode == ExchangeMode.DEMO:
            self._exchange.enable_demo_trading(True)

    @property
    def exchange(self):
        return self._exchange

    async def read_ohlcv_data(
        self, symbol: str, timeframe: TimeFrame, limit: int
    ) -> OhlcvData:
        """
        Args
            symbol:
            timeframe:
            limit:
        Returns:
            list[list[float]]: A list of candles ordered: timestamp, open, high, low, close, volume
        """
        return await self._exchange.fetch_mark_ohlcv(
            symbol, timeframe=timeframe.value, limit=limit
        )

    async def read_latest_trades(self, symbols: list[str]) -> list[ExchangeTrade]:
        if not symbols:
            return []
        trades = (
            await self._exchange.watch_trades_for_symbols(symbols)
            if len(symbols) > 1
            else await self._exchange.watch_trades(symbols[0])
        )
        return list(
            map(
                lambda t: ExchangeTrade(
                    symbol=t["symbol"],
                    side=(
                        ExchangeTradeSide.BUY
                        if t["side"] == "buy"
                        else ExchangeTradeSide.SELL
                    ),
                    price=t["price"],
                    amount=t["amount"],
                    timestamp=t["timestamp"],  # milliseconds
                ),
                trades,
            )
        )

    async def close(self):
        await self._exchange.close()
