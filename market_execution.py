import logging
import asyncio
import json
import os

from deal.deal import Deal
from deal.entities import DealState
from entities import StorageConfig, DealConfig
from exceptions import GeneralAppException
from gp_config import GPConfig
from market_data_analyzer import MarketDataAnalyzer
from market_data_collector import MarketDataCollector
from trades_storage import TradesStorage
from indicators.indicators_pool import IndicatorsPool

logger = logging.getLogger(__name__)

DEAL_STATE_FILE = "deal_state.json"

_trade_storage: TradesStorage | None = None
_deal: Deal | None = None
_indicators_pool: IndicatorsPool | None = None


def _init_trade_storage(config: StorageConfig) -> TradesStorage:
    global _trade_storage
    if _trade_storage:
        return _trade_storage

    _trade_storage = TradesStorage(config)
    return _trade_storage


def _get_trade_storage() -> TradesStorage:
    global _trade_storage
    if not _trade_storage:
        raise GeneralAppException("Trade storage was not initialized")
    return _trade_storage


def _init_indicators_pool(storage: TradesStorage) -> IndicatorsPool:
    global _indicators_pool
    if _indicators_pool:
        raise GeneralAppException("Indicators pool has already been created")

    _indicators_pool = IndicatorsPool(storage)
    return _indicators_pool


def _get_indicators_pool() -> IndicatorsPool:
    global _indicators_pool
    if not _indicators_pool:
        raise GeneralAppException("Indicators pool was not created")
    return _indicators_pool


def _init_deal(
    working_dir: str, deal_config: DealConfig, indicators_pool: IndicatorsPool
):
    global _deal
    if _deal:
        raise GeneralAppException("Deal has already been initialized")

    deal_state_file = os.path.join(working_dir, DEAL_STATE_FILE)
    deal_state = None
    if os.path.isfile(deal_state_file):
        with open(deal_state_file, "r") as f:
            data = json.load(f)
            deal_state = DealState(**data)

    _deal = Deal(deal_config, indicators_pool, deal_state)


def _get_deal() -> Deal:
    global _deal
    if not _deal:
        raise GeneralAppException("Deal was not initialized")
    return _deal


def _save_deal(working_dir: str):
    global _deal
    if not _deal:
        raise GeneralAppException("Deal was not initialized")

    deal_state_file = os.path.join(working_dir, DEAL_STATE_FILE)
    with open(deal_state_file, "w", encoding="utf-8") as f:
        data = _deal.state.model_dump()
        json.dump(data, f)


def init_market_execution(config: GPConfig, working_dir: str):
    trade_storage = _init_trade_storage(config.storage)
    indicators_pool = _init_indicators_pool(trade_storage)
    _init_deal(working_dir, config.deal, indicators_pool)


async def reading_market_trades(config: GPConfig):
    logger.info("Trades reading started")

    trade_storage = _get_trade_storage()
    data_collector = MarketDataCollector(config.exchange, config.market.symbol, _get_indicators_pool())
    try:
        # Prepare initial ohlcv data according to filters' demands
        logger.info("Collecting initial data...")
        tf_ohlcv_data = await data_collector.collect_initial_data()
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
        trade_storage = _get_trade_storage()
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
