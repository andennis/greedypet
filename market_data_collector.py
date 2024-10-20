from collections import defaultdict
from data_reader import ExchangeDataReader
from entities import ExitMode, TimeFrame, Filter, Trade
from gp_config import GPConfig
from filters import filter_factory


class MarketDataCollector:
    def __init__(self, config: GPConfig):
        self._config = config
        self._reader = ExchangeDataReader(config.exchange)

    @staticmethod
    def _get_data_to_read(timeframe_map: dict[TimeFrame, int], filters: list[Filter]):
        for flt in map(filter_factory.create_filter, filters):
            timeframe_map[flt.time_frame] = max(
                timeframe_map[flt.time_frame], max(flt.all_periods)
            )

    async def collect_initial_data(self) -> dict[TimeFrame, list[list[float]]]:
        timeframe_map = defaultdict(int)
        self._get_data_to_read(timeframe_map, self._config.entry_condition.filters)
        if (
            self._config.exit_condition.mode == ExitMode.SIGNAL
            and self._config.exit_condition.signal
        ):
            self._get_data_to_read(
                timeframe_map, self._config.exit_condition.signal.filters
            )

        result: dict[TimeFrame, list[list[float]]] = dict()
        for time_frame, periods in timeframe_map.items():
            result[time_frame] = await self._reader.read_ohlcv_data(
                self._config.market.symbol, time_frame, periods
            )

        return result

    async def collect_trades(self) -> list[Trade]:
        return await self._reader.read_latest_trades(self._config.market.symbol)
