import yaml
import logging
from pydantic import BaseModel
from entities import Exchange, ExchangeMarket, DealConfig, StorageConfig

logger = logging.getLogger(__name__)


class GPConfig(BaseModel):
    exchange: Exchange
    market: ExchangeMarket
    deal: DealConfig
    storage: StorageConfig | None = None


def load_config(file_name: str):
    with open(file_name, "r") as f:
        cfg = yaml.safe_load(f)
        config = GPConfig(**cfg)
        logger.info(f"Config loaded from {file_name}")
        return config
