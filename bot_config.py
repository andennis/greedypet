import yaml
import logging
from pydantic import BaseModel
from entities import Exchange, ExchangeMarket, TradeAlgorithm, EntryCondition, ExitCondition

logger = logging.getLogger(__name__)


class GPConfig(BaseModel):
    exchange: Exchange
    market: ExchangeMarket
    trade_algorithm: TradeAlgorithm
    entry_condition: EntryCondition
    exit_condition: ExitCondition


GP_CONFIG:  GPConfig


def load_config(file_name: str):
    with open(file_name, "r") as f:
        cfg = yaml.safe_load(f)
        logger.info(f"Config loaded from {file_name}")
        global GP_CONFIG
        GP_CONFIG = GPConfig(**cfg)
