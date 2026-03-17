from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    MODEL_PATH: str = "/app/model/yolov8n.pt"
    UPLOAD_DIR: str = "/app/uploads"

    class Config:
        env_file = ".env"


settings = Settings()