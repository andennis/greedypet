import pytest

from caterpillar.dal.models.currency_pair import CurrencyPair


@pytest.mark.asyncio
async def test_add_pair(clean_db, repo_pair):
    pair = repo_pair.add("BTC/USDT")
    await repo_pair.commit()

    assert isinstance(pair, CurrencyPair)
    assert pair.name == "BTC/USDT"
    assert pair.is_active is True


@pytest.mark.asyncio
async def test_get_pairs(clean_db, repo_pair):
    repo_pair.add("BTC/USDT")
    repo_pair.add("ETH/USDT")
    await repo_pair.commit()

    # Make one inactive
    pairs = await repo_pair.get_list()
    pairs[0].is_active = False
    await repo_pair.commit()

    all_pairs = await repo_pair.get_list()
    assert len(all_pairs) == 2

    active_pairs = await repo_pair.get_active()
    assert len(active_pairs) == 1
    assert active_pairs[0].name == "ETH/USDT"
    pair = await repo_pair.get(pair_id=active_pairs[0].pair_id)
    assert pair
    assert pair.name == active_pairs[0].name


@pytest.mark.asyncio
async def test_delete_pair(clean_db, repo_pair):
    pair = repo_pair.add("BTC/USDT")
    await repo_pair.commit()

    await repo_pair.delete(pair)
    await repo_pair.commit()

    # Verify deletion
    pairs = await repo_pair.get_list()
    assert len(pairs) == 0
