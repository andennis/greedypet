import pytest_asyncio
from entities import Exchange, ExchangeId, TradingMode
from dotenv import load_dotenv
from exchange_data_reader import ExchangeDataReader

load_dotenv()


@pytest_asyncio.fixture
async def data_reader_sandbox():
    dr = ExchangeDataReader(Exchange(id=ExchangeId.BYBIT, trading_mode=TradingMode.SANDBOX))
    try:
        yield dr
    finally:
        await dr.close()


@pytest_asyncio.fixture
async def data_reader_demo():
    dr = ExchangeDataReader(Exchange(id=ExchangeId.BYBIT, trading_mode=TradingMode.DEMO))
    try:
        yield dr
    finally:
        await dr.close()
