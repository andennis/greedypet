from pydantic import computed_field, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GRPT_DB_", env_ignore_empty=True, extra="ignore"
    )

    host: str = "localhost"
    port: int = 5432
    database: str = Field(default="greedypet", alias="GRPT_DB_NAME")
    username: str = Field(default="greedypet", alias="GRPT_DB_USER")
    password: str = "greedypet"
    log_db_request: bool = Field(default=False, alias="GRPT_DB_LOG_REQUESTS")

    @computed_field
    @property
    def connection(self) -> str:
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
