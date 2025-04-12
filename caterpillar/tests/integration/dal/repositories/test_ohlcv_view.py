import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import create_async_engine

from caterpillar.dal.models.trade import TradeSide, Trade


async def _refresh_continuous_aggregate(db_url: str):
    engine = create_async_engine(db_url)
    start_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    end_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    async with engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        proc_call = text(f"CALL refresh_continuous_aggregate('trades_1min_ohlcv', '{start_time}', '{end_time}');")
        await conn.execute(proc_call)
    await engine.dispose()


@pytest_asyncio.fixture
async def setup_trades(repo_ohlcv, repo_pair, repo_trade, clean_db, db_conn_url):
    await _refresh_continuous_aggregate(db_conn_url)
    # Create pair
    pair = repo_pair.add("BTC/USDT")
    await repo_pair.commit()

    # Add trades
    now = datetime.now(timezone.utc)
    trades_data = [
        {
            "pair_id": pair.pair_id,
            "price": Decimal("50000.00"),
            "volume": Decimal("1.0"),
            "side": TradeSide.BUY,
            "timestamp": now - timedelta(seconds=100)
        },
        {
            "pair_id": pair.pair_id,
            "price": Decimal("50100.00"),
            "volume": Decimal("0.5"),
            "side": TradeSide.SELL,
            "timestamp": now - timedelta(seconds=95)
        }
    ]
    for trade in trades_data:
        repo_trade.create(Trade(**trade))
    await repo_trade.commit()
    return pair


@pytest.mark.asyncio
async def test_get_candles(repo_ohlcv, setup_trades, db_conn_url):
    await _refresh_continuous_aggregate(db_conn_url)

    now = datetime.now(timezone.utc)
    candles = await repo_ohlcv.get_candles(
        pair_id=setup_trades.pair_id,
        start_time=now - timedelta(minutes=100),
        end_time=now + timedelta(minutes=100)
    )

    assert len(candles) > 0
    candle = candles[0]
    assert candle.open == Decimal("50000.00")
    assert candle.high == Decimal("50100.00")
    assert candle.low == Decimal("50000.00")
    assert candle.close == Decimal("50100.00")
    assert candle.buy_volume == Decimal("1.0")
    assert candle.sell_volume == Decimal("0.5")
    assert candle.total_volume == Decimal("1.5")
    assert candle.buy_trades == 1
    assert candle.sell_trades == 1
    assert candle.total_trades == 2
