from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Liderancas Empaticas API"
    ENV: str = "local"

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/app"

    JWT_SECRET: str = "CHANGE_ME"
    JWT_ALG: str = "HS256"
    JWT_EXPIRES_MIN: int = 60 * 24  # 24h

    ALLOWED_ORIGINS: str = "*"  # em prod, coloque seu domínio do app web se tiver

    class Config:
        env_file = ".env"


settings = Settings()