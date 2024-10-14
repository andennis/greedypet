import pytest_asyncio
from entities import Exchange, ExchangeId
from dotenv import load_dotenv
from data_reader import ExchangeDataReader

load_dotenv()


@pytest_asyncio.fixture
async def data_reader():
    dr = ExchangeDataReader(Exchange(id=ExchangeId.BYBIT))
    try:
        yield dr
    finally:
        await dr.close()
