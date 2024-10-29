import logging
import asyncio
# from tenacity import retry, stop_after_attempt, retry_if_not_exception_type, RetryCallState
from gp_config import GPConfig
from market_data_collector import MarketDataCollector
from trades_storage import TradesStorage

logger = logging.getLogger(__name__)


# def retry_stop_app(retry_state: RetryCallState):
#     return retry_state.outcome.result()


# @retry(
#     stop=stop_after_attempt(3),
#     retry=retry_if_not_exception_type(asyncio.CancelledError),
#     # retry_error_callback=retry_stop_app,
# )
async def reading_market_trades(config: GPConfig):
    logger.info(f"Trades reading started")
    data_collector = MarketDataCollector(config)
    try:
        # Prepare initial ohlcv data according to filters' demands
        logger.info(f"Collecting initial data...")
        tf_ohlcv_data = await data_collector.collect_initial_data()
        trade_storage = TradesStorage(config.storage, config.market.symbol)
        for tf, ohlcv_data in tf_ohlcv_data.items():
            trade_storage.upload_initial_ohlcv_data(tf, ohlcv_data)
        logger.info(f"Initial data has been collected")

        # Run trades gathering
        while True:
            logger.info(f"Waiting for trades...")
            trades = await data_collector.collect_trades()
            logger.info(f"New trades received")
            for trade in trades:
                trade_storage.add_trade(trade)
            await asyncio.sleep(1)

    except asyncio.CancelledError:
        logger.info(f"Trades reading finished")
    finally:
        await data_collector.close()


# @retry(
#     stop=stop_after_attempt(3),
#     retry=retry_if_not_exception_type(asyncio.CancelledError),
#     # retry_error_callback=retry_stop_app,
# )
async def tracking_trade_signals(config: GPConfig):
    logger.info(f"Trade signals tracking started")
    try:
        while True:
            logger.info(f"Track trade signals")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info(f"Trade signals tracking finished")


# @retry(
#     stop=stop_after_attempt(3),
#     retry=retry_if_not_exception_type(asyncio.CancelledError),
#     # retry_error_callback=retry_stop_app,
# )
async def making_market_trades(config: GPConfig):
    logger.info(f"Trading started")
    try:
        while True:
            logger.info(f"Make trading")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info(f"Trading finished")
