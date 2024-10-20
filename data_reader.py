import os
import ccxt.pro as ccxt
from entities import TimeFrame, Exchange, Trade, TradeSide, TradingMode


class ExchangeDataReader:
    def __init__(self, exchange_config: Exchange):
        exchange_class = getattr(ccxt, exchange_config.id.value)
        self._exchange = exchange_class(
            {
                "apiKey": os.environ.get("GP_API_KEY", exchange_config.api_key),
                "secret": os.environ.get("GP_API_SECRET", exchange_config.api_secret),
            }
        )
        if exchange_config.trading_mode == TradingMode.SANDBOX:
            self._exchange.set_sandbox_mode(True)
        elif exchange_config.trading_mode == TradingMode.DEMO:
            self._exchange.enable_demo_trading(True)

    @property
    def exchange(self):
        return self._exchange

    async def read_ohlcv_data(
        self, symbol: str, time_frame: TimeFrame, limit: int
    ) -> list[list[float]]:
        """
        :param symbol:
        :param time_frame:
        :param limit:
        :return: list[list[float]]: A list of candles ordered: timestamp, open, high, low, close, volume
        """
        return await self._exchange.fetch_mark_ohlcv(
            symbol, timeframe=time_frame.value, limit=limit
        )

    async def read_latest_trades(self, symbol: str) -> list[Trade]:
        trades = await self._exchange.watch_trades(symbol)
        return list(
            map(
                lambda t: Trade(
                    side=TradeSide.BUY if t["side"] == "buy" else TradeSide.SELL,
                    price=t["price"],
                    amount=t["amount"],
                    timestamp=t["timestamp"],
                ),
                trades,
            )
        )

    async def close(self):
        await self._exchange.close()
