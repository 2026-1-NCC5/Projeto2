from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    CAMERA_API_KEY: str = "camera-secret-key"

    class Config:
        env_file = ".env"


settings = Settings()
