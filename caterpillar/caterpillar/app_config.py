import logging
from pydantic import BaseModel

from common.exchange.entities import ExchangeConfig, ExchangeId
from common.db.config import DatabaseConfig

logger = logging.getLogger(__name__)


class AppConfig(BaseModel):
    exchange: ExchangeConfig
    database: DatabaseConfig


def load_config(file_name: str):
    return AppConfig(
        exchange=ExchangeConfig(),
        database=DatabaseConfig()
    )
