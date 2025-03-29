from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os

env_name = os.getenv("ENV_APP", "development")
base_dir = Path(__file__).resolve().parent
env_path = base_dir / f".env.{env_name}"

class Settings(BaseSettings):
    ENV_APP: str = env_name
    DB_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    ALGORITHM: str
    SECRET_KEY: str

    CLD_NAME: str
    CLD_API_KEY: int
    CLD_API_SECRET: str

    model_config = ConfigDict(
        env_file=env_path,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
