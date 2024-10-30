import yaml
import logging
from pydantic import BaseModel
from entities import Exchange, ExchangeMarket, TradeAlgorithm, EntryCondition, ExitCondition, StorageConfig

logger = logging.getLogger(__name__)


class GPConfig(BaseModel):
    exchange: Exchange
    market: ExchangeMarket
    trade_algorithm: TradeAlgorithm = TradeAlgorithm.LONG
    entry_condition: EntryCondition
    exit_condition: ExitCondition
    storage: StorageConfig | None = None


def load_config(file_name: str):
    with open(file_name, "r") as f:
        cfg = yaml.safe_load(f)
        config = GPConfig(**cfg)
        logger.info(f"Config loaded from {file_name}")
        return config
