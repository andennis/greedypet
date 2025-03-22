import os

import pytest
import pytest_asyncio

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from caterpillar.dal.db_client import DbClient

load_dotenv()


# @pytest_asyncio.fixture(scope="session")
# async def setup_test_db():
#     """Setup test database with required tables."""
#     engine = create_async_engine(TEST_DB_URL)
#
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#         # await conn.execute(text("SELECT create_hypertable('trades', 'timestamp')"))
#
#     await engine.dispose()

@pytest.fixture
def db_conn_url():
    return os.environ["GP_TEST_DB_URL"]


@pytest_asyncio.fixture
async def clean_db(db_conn_url):
    engine = create_async_engine(db_conn_url)
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE currency_pairs CASCADE"))
        await conn.execute(text("TRUNCATE TABLE trades CASCADE"))
    await engine.dispose()


@pytest_asyncio.fixture
async def db_client(db_conn_url):
    async with DbClient(db_conn_url) as client:
        yield client
