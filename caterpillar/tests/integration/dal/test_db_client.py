import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_session_context(db_client):
    async with db_client.session() as session:
        assert isinstance(session, AsyncSession)
        result = await session.execute(select(1))
        assert result.scalar() == 1
