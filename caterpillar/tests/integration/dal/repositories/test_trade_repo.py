import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from caterpillar.dal.models.trade import Trade, TradeSide


@pytest_asyncio.fixture
async def btc_pair(repo_pair, clean_db):
    pair = repo_pair.add("BTC/USDT")
    await repo_pair.commit()
    return pair


@pytest.mark.asyncio
async def test_add_delete_trade(repo_trade, btc_pair):
    new_trade = Trade(
        pair_id=btc_pair.pair_id,
        price=Decimal("50000.00"),
        volume=Decimal("1.5"),
        side=TradeSide.BUY,
        timestamp=datetime.now(timezone.utc)
    )

    trade = repo_trade.create(new_trade)
    await repo_trade.commit()

    assert isinstance(trade, Trade)
    assert trade.price == new_trade.price
    assert trade.volume == new_trade.volume
    assert trade.side == new_trade.side

    await repo_trade.delete(trade)
    await repo_trade.commit()


@pytest.mark.asyncio
async def test_get_filtered_trades(repo_trade, btc_pair):
    # Add trades with different timestamps
    now = datetime.now(timezone.utc)
    trade1 = repo_trade.create(Trade(
        pair_id=btc_pair.pair_id,
        price=Decimal("50000.00"),
        volume=Decimal("1.0"),
        side=TradeSide.BUY,
        timestamp=now - timedelta(hours=2)
    ))
    trade2 = repo_trade.create(Trade(
        pair_id=btc_pair.pair_id,
        price=Decimal("51000.00"),
        volume=Decimal("1.0"),
        side=TradeSide.SELL,
        timestamp=now
    ))
    await repo_trade.commit()

    # Test time filtering
    recent_trades = await repo_trade.get_filtered(pair_id=btc_pair.pair_id)
    assert len(recent_trades) == 2

    recent_trades = await repo_trade.get_filtered(
        pair_id=btc_pair.pair_id,
        start_time=now - timedelta(hours=1)
    )
    assert len(recent_trades) == 1
    assert recent_trades[0].timestamp == trade2.timestamp

    await repo_trade.delete(trade1)
    await repo_trade.delete(trade2)
    await repo_trade.commit()
    recent_trades = await repo_trade.get_filtered(
        pair_id=btc_pair.pair_id,
    )
    assert len(recent_trades) == 0



