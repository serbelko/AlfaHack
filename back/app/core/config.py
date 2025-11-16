from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str | None = None
    ASYNC_DATABASE_URL: str | None = None
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
    def ASYNC_DATABASE_URL_computed(self) -> str:
        """Вычисляемый URL для основной БД, использует имя сервиса 'db' в Docker"""
        if self.ASYNC_DATABASE_URL:
            return self.ASYNC_DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def MOCK_ASYNC_DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.MOCK_POSTGRES_USER}:{self.MOCK_POSTGRES_PASSWORD}"
            f"@{self.MOCK_POSTGRES_HOST}:{self.MOCK_POSTGRES_PORT}/{self.MOCK_POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()