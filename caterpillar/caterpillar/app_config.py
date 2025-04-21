import logging

from dotenv import load_dotenv
from pydantic import BaseModel

from grpt_common.exchange.entities import ExchangeConfig, ExchangeId
from grpt_common.db.config import DatabaseConfig

load_dotenv()
logger = logging.getLogger(__name__)


class AppConfig(BaseModel):
    exchange: ExchangeConfig
    database: DatabaseConfig


def load_config(file_name: str):
    return AppConfig(
        exchange=ExchangeConfig(),
        database=DatabaseConfig()
    )
