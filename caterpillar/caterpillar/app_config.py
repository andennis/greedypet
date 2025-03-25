import logging
import yaml
from pydantic import BaseModel

from common.exchange.entities import ExchangeConfig

logger = logging.getLogger(__name__)


class DataBaseConfig(BaseModel):
    connection: str


class AppConfig(BaseModel):
    exchange: ExchangeConfig
    database: DataBaseConfig


def load_config(file_name: str):
    with open(file_name, "r") as f:
        cfg = yaml.safe_load(f)
        config = AppConfig(**cfg)
        logger.info(f"Config loaded from {file_name}")
        return config
