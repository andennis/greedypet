import pytest_asyncio

from caterpillar.dal.repositories.currency_pair_repo import CurrencyPairRepository
from caterpillar.dal.repositories.ohlcv_view import OHLCVViewRepository
from caterpillar.dal.repositories.trade_repo import TradeRepository


@pytest_asyncio.fixture
async def repo_pair(db_client):
    async with db_client.session() as session:
        yield CurrencyPairRepository(session)


@pytest_asyncio.fixture
async def repo_trade(db_client):
    async with db_client.session() as session:
        yield TradeRepository(session)


@pytest_asyncio.fixture
async def repo_ohlcv(db_client):
    async with db_client.session() as session:
        yield OHLCVViewRepository(session)
