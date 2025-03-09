import pytest

from caterpillar.dal.models.currency_pair import CurrencyPair


# @pytest.mark.asyncio
# async def test1(clean_db):
#     async with DbClient(TEST_DB_URL) as client:
#         async with client.session() as conn:
#             rep = CurrencyPairRepository(conn)
#             await rep.add("BTC", "USDT")
#             await rep.add("ETH", "USDT")
#             await conn.commit()
#
#         async with client.session() as session:
#             rep = CurrencyPairRepository(session)
#             await rep.add("SOL", "USDT")
#             await rep.get_all()
#             await session.commit()


@pytest.mark.asyncio
async def test_add_currency_pair(clean_db, repo_pair):
    pair = await repo_pair.add("BTC", "USD")
    await repo_pair.commit()

    assert isinstance(pair, CurrencyPair)
    assert pair.base_currency == "BTC"
    assert pair.quote_currency == "USD"
    assert pair.is_active is True


@pytest.mark.asyncio
async def test_get_pairs(clean_db, repo_pair):
    await repo_pair.add("BTC", "USDT")
    await repo_pair.add("ETH", "USDT")
    await repo_pair.commit()

    # Make one inactive
    pairs = await repo_pair.get_list()
    pairs[0].is_active = False
    await repo_pair.commit()

    all_pairs = await repo_pair.get_list()
    assert len(all_pairs) == 2

    active_pairs = await repo_pair.get_active()
    assert len(active_pairs) == 1
    assert active_pairs[0].base_currency == "ETH"
    pair = await repo_pair.get(pair_id=active_pairs[0].pair_id)
    assert pair
    assert pair.quote_currency == active_pairs[0].quote_currency


@pytest.mark.asyncio
async def test_delete_pair(clean_db, repo_pair):
    pair = await repo_pair.add("BTC", "USD")
    await repo_pair.commit()

    await repo_pair.delete(pair)
    await repo_pair.commit()

    # Verify deletion
    pairs = await repo_pair.get_list()
    assert len(pairs) == 0
