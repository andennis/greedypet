from collections import defaultdict
from exchange_data_reader import ExchangeDataReader
from entities import ExitMode, TimeFrame, FilterConfig, Trade, OhlcvData
from gp_config import GPConfig
from filters import filter_factory


class MarketDataCollector:
    def __init__(self, config: GPConfig):
        self._config = config
        self._reader = ExchangeDataReader(config.exchange)

    @staticmethod
    def _get_max_timeframes_len(filters: list[FilterConfig]) -> dict[TimeFrame, int]:
        """
        Retrieve from filters all the time frames and their max length required by the filter
        Args:
            filters (list[FilterConfig]): list of filters
        Returns:
            dict[TimeFrame, int]: dict of time frames (TimeFrame) mapped to number of the time frames periods
        """
        timeframe_map = defaultdict(int)
        for flt in map(filter_factory.create_filter, filters):
            timeframe_map[flt.time_frame] = max(
                timeframe_map[flt.time_frame], max(flt.all_periods)
            )
        return timeframe_map

    async def collect_initial_data(self) -> dict[TimeFrame, OhlcvData]:
        """
        Read initial data from exchange according to filters demands.
        Each filter requires the series of latest ohlcv time frames.
        These series with specified time frames are loaded from exchange

        Returns:
            dict[TimeFrame, OhlcvData]: dict of OhlcvData.
                Dict key is TimeFrame.
                Dict value is OhlcvData which is list of float lists.
                Each float list contains the following six elements:
                    [timestamp (milliseconds), open, high, low, close, volume]
        """
        filters = self._config.deal.entry_condition.filters
        if self._config.deal.exit_condition.mode == ExitMode.SIGNAL:
            filters.extend(self._config.deal.exit_condition.signal.filters)

        timeframe_map = self._get_max_timeframes_len(filters)

        result: dict[TimeFrame, OhlcvData] = dict()
        for time_frame, periods in timeframe_map.items():
            result[time_frame] = await self._reader.read_ohlcv_data(
                self._config.market.symbol, time_frame, periods
            )

        return result

    async def collect_trades(self) -> list[Trade]:
        return await self._reader.read_latest_trades(self._config.market.symbol)

    async def close(self):
        await self._reader.close()
