import logging
import asyncio
# from tenacity import retry, stop_after_attempt, retry_if_not_exception_type, RetryCallState
from gp_config import GPConfig
from market_data_analyzer import MarketDataAnalyzer
from market_data_collector import MarketDataCollector
from trades_storage import TradesStorage


logger = logging.getLogger(__name__)
_trade_storage: TradesStorage | None = None


def _get_trade_storage(config: GPConfig) -> TradesStorage:
    global _trade_storage
    if not _trade_storage:
        _trade_storage = TradesStorage(config.storage, config.market.symbol)
    return _trade_storage


async def reading_market_trades(config: GPConfig):
    logger.info("Trades reading started")
    data_collector = MarketDataCollector(config)
    try:
        # Prepare initial ohlcv data according to filters' demands
        logger.info("Collecting initial data...")
        tf_ohlcv_data = await data_collector.collect_initial_data()
        trade_storage = _get_trade_storage(config)
        for tf, ohlcv_data in tf_ohlcv_data.items():
            trade_storage.upload_initial_ohlcv_data(tf, ohlcv_data)
        logger.info("Initial data has been collected")

        # Run trades gathering
        while True:
            logger.info("Waiting for trades...")
            trades = await data_collector.collect_trades()
            logger.info("New trades received")
            for trade in trades:
                trade_storage.add_trade(trade)
            # await asyncio.sleep(1)

    except asyncio.CancelledError:
        logger.info("Trades reading finished")
    finally:
        await data_collector.close()


async def tracking_trade_signals(config: GPConfig):
    logger.info("Trade signals tracking started")
    try:
        trade_storage = _get_trade_storage(config)
        data_analyzer = MarketDataAnalyzer(config.deal, trade_storage)
        while True:
            logger.info("Wait for next timeframe")
            await data_analyzer.sleep_to_next_timeframe()
    except asyncio.CancelledError:
        logger.info("Trade signals tracking finished")


async def making_market_trades(config: GPConfig):
    logger.info("Trading started")
    try:
        while True:
            logger.info("Make trading")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Trading finished")
