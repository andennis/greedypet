from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


class DbClient:
    """
    Async client for managing database connection.
    """

    def __init__(self, dsn: str, log_db_request: bool = False):
        """
        Initialize DB client

        Args:
            dsn: Database connection string in format:
                postgresql+asyncpg://user:password@host:port/dbname
        """
        self._engine = create_async_engine(dsn, echo=log_db_request)
        self._session_maker = async_sessionmaker(self._engine, expire_on_commit=False)

    async def close(self) -> None:
        """Close database connection and release all resources."""
        await self._engine.dispose()

    def session(self) -> AsyncSession:
        return self._session_maker()

    async def __aenter__(self) -> "DbClient":
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        await self.close()
