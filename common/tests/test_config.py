import os
from unittest.mock import patch

from common.db.config import DatabaseConfig
from common.exchange.entities import ExchangeConfig, ExchangeId, ExchangeMode


@patch.dict(os.environ, clear=True)
def test_config_default():
    db_config = DatabaseConfig()
    assert db_config.host == "localhost"
    assert db_config.port == 5432
    assert db_config.database == "greedypet"
    assert db_config.username == "greedypet"
    assert db_config.password == "greedypet"
    assert db_config.log_db_request is False


@patch.dict(
    os.environ,
    {
        "GRPT_DB_HOST": "1.2.3.4",
        "GRPT_DB_PORT": "1111",
        "GRPT_DB_NAME": "my-db",
        "GRPT_DB_USER": "my-user",
        "GRPT_DB_PASSWORD": "my-psw",
        "GRPT_DB_LOG_REQUESTS": "True",
    },
)
def test_config_specific():
    db_config = DatabaseConfig()
    assert db_config.host == "1.2.3.4"
    assert db_config.port == 1111
    assert db_config.database == "my-db"
    assert db_config.username == "my-user"
    assert db_config.password == "my-psw"
    assert db_config.log_db_request is True
    assert (
        db_config.connection == "postgresql+asyncpg://my-user:my-psw@1.2.3.4:1111/my-db"
    )


@patch.dict(os.environ, clear=True)
def test_exchange_config_default():
    config = ExchangeConfig()
    assert config.id == ExchangeId.BYBIT
    assert config.mode == ExchangeMode.REAL
    assert config.api_key is None
    assert config.api_secret is None


@patch.dict(
    os.environ,
    {
        "GRPT_EXCHANGE_MODE": "demo",
        "GRPT_EXCHANGE_API_KEY": "key1",
        "GRPT_EXCHANGE_API_SECRET": "scrt1",
    },
)
def test_exchange_config_specific():
    config = ExchangeConfig()
    assert config.mode == ExchangeMode.DEMO
    assert config.api_key == "key1"
    assert config.api_secret == "scrt1"
