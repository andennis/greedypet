from collections import defaultdict
from exchange_data_reader import ExchangeDataReader
from entities import TimeFrame, Trade, OhlcvData, ExchangeConfig
from indicators.indicators_pool import IndicatorsPool


class MarketDataCollector:
    def __init__(self, config: ExchangeConfig, symbol: str, indicators_pool: IndicatorsPool):
        self._symbol = symbol
        self._indicators_pool = indicators_pool
        self._reader = ExchangeDataReader(config)

    def _get_max_timeframes_len(self) -> dict[TimeFrame, int]:
        """
        Retrieve max indicator periods value in scope of timeframe

        Returns:
            dict[TimeFrame, int]: dict of time frames (TimeFrame) mapped to number of the time frames periods
        """
        timeframe_map = defaultdict(int)
        for tf in self._indicators_pool.timeframes:
            for indicator in self._indicators_pool.get_indicators(tf):
                timeframe_map[tf] = max(timeframe_map[tf], indicator.periods)
        return timeframe_map

    async def collect_initial_data(self) -> dict[TimeFrame, OhlcvData]:
        """
        Read initial data from the exchange according to indicators demands (e.g. periods number).
        Each indicator requires the series of latest ohlcv time frames.
        These series with specified time frames are loaded from the exchange

        Returns:
            dict[TimeFrame, OhlcvData]: dict of OhlcvData.
                Dict key is TimeFrame.
                Dict value is OhlcvData which is list of float lists.
                Each float list contains the following six elements:
                    [timestamp (milliseconds), open, high, low, close, volume]
        """
        timeframe_map = self._get_max_timeframes_len()
        result: dict[TimeFrame, OhlcvData] = dict()
        for time_frame, periods in timeframe_map.items():
            result[time_frame] = await self._reader.read_ohlcv_data(
                self._symbol, time_frame, periods + 1
            )

        return result

    async def collect_trades(self) -> list[Trade]:
        return await self._reader.read_latest_trades(self._symbol)

    async def close(self):
        await self._reader.close()
