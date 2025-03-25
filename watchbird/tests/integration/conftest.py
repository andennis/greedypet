import pytest_asyncio
from watchbird.entities import ExchangeConfig, ExchangeId, ExchangeMode
from dotenv import load_dotenv
from watchbird.exchange_data_reader import ExchangeDataReader

load_dotenv()


@pytest_asyncio.fixture
async def data_reader_sandbox():
    dr = ExchangeDataReader(ExchangeConfig(id=ExchangeId.BYBIT, trading_mode=ExchangeMode.SANDBOX))
    try:
        yield dr
    finally:
        await dr.close()


@pytest_asyncio.fixture
async def data_reader_demo():
    dr = ExchangeDataReader(ExchangeConfig(id=ExchangeId.BYBIT, trading_mode=ExchangeMode.DEMO))
    try:
        yield dr
    finally:
        await dr.close()
