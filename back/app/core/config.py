from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str
    ASYNC_DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SECRET_KEY: str
    PASSWORD_MIN_LENGTH: int
    ALGORITHM: str = "HS256"
    ISSUER: str | None = None 
    AUDIENCE: str | None = None
    REDIS_URL: str | None = None
    
    # Mock DB settings
    MOCK_POSTGRES_HOST: str = "mock_db"
    MOCK_POSTGRES_PORT: int = 5432
    MOCK_POSTGRES_USER: str
    MOCK_POSTGRES_PASSWORD: str
    MOCK_POSTGRES_DB: str

    @property
    def MOCK_ASYNC_DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.MOCK_POSTGRES_USER}:{self.MOCK_POSTGRES_PASSWORD}"
            f"@{self.MOCK_POSTGRES_HOST}:{self.MOCK_POSTGRES_PORT}/{self.MOCK_POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()