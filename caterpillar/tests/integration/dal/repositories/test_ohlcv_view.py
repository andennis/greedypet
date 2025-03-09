# import asyncio
# import pytest
# import pytest_asyncio
# from datetime import datetime, timedelta, timezone
# from decimal import Decimal
#
# from pycparser.c_ast import While
#
# from dal.models.trade import TradeSide, Trade
#
#
# @pytest_asyncio.fixture
# async def setup_trades(repo_ohlcv, repo_pair, repo_trade, clean_db):
#     for _ in range(10):
#         await asyncio.sleep(2)
#
#         now = datetime.now(timezone.utc)
#         candles = await repo_ohlcv.get_list()
#         if not candles:
#             break
#
#     # Create pair
#     pair = await repo_pair.add("BTC", "USD")
#     await repo_pair.commit()
#
#     # Add trades
#     now = datetime.now(timezone.utc)
#     trades_data = [
#         {
#             "pair_id": pair.pair_id,
#             "price": Decimal("50000.00"),
#             "volume": Decimal("1.0"),
#             "side": TradeSide.BUY,
#             "timestamp": now - timedelta(minutes=5)
#         },
#         {
#             "pair_id": pair.pair_id,
#             "price": Decimal("50100.00"),
#             "volume": Decimal("0.5"),
#             "side": TradeSide.SELL,
#             "timestamp": now - timedelta(minutes=3)
#         }
#     ]
#     for trade in trades_data:
#         await repo_trade.create(Trade(**trade))
#     await repo_trade.commit()
#     return pair
#
#
# @pytest.mark.asyncio
# async def test_get_candles(repo_ohlcv, setup_trades):
#     # Wait for continuous aggregate to process
#     candles = []
#     for _ in range(10):
#         await asyncio.sleep(2)
#
#         now = datetime.now(timezone.utc)
#         candles = await repo_ohlcv.get_candles(
#             pair_id=setup_trades.pair_id,
#             start_time=now - timedelta(minutes=100),
#             end_time=now + timedelta(minutes=100)
#         )
#         if len(candles) > 0:
#             break
#
#     assert len(candles) > 0
#     candle = candles[0]
#     assert candle.open == Decimal("50000.00")
#     assert candle.high == Decimal("50100.00")
#     assert candle.low == Decimal("50000.00")
#     assert candle.close == Decimal("50100.00")
#     assert candle.volume == Decimal("1.5")
#     assert candle.number_of_trades == 2
