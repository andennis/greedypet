import logging
import yaml
from pydantic import BaseModel

from entities import ExchangeConfig, ExchangeMarket

logger = logging.getLogger(__name__)


class AppConfig(BaseModel):
    exchange: ExchangeConfig
    market: ExchangeMarket


def load_config(file_name: str):
    with open(file_name, "r") as f:
        cfg = yaml.safe_load(f)
        config = AppConfig(**cfg)
        logger.info(f"Config loaded from {file_name}")
        return config

