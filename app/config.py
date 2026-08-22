import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    BOT_TOKEN: str = ""
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WEBAPP_URL: str = "http://localhost:8000"


    DAILY_REPORT_TIME: str = "20:00"
    TIMEZONE: str = "Europe/Warsaw"

    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/data/bot_tasks.db"

    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    @property
    def effective_gemini_api_key(self) -> str:
        return (
            self.GEMINI_API_KEY or
            os.environ.get("GEMINI_API_KEY", "") or
            os.environ.get("GOOGLE_API_KEY", "") or
            os.environ.get("GEMINI_KEY", "") or
            os.environ.get("GOOGLE_GEMINI_API_KEY", "")
        ).strip()

    @property
    def effective_openai_api_key(self) -> str:
        return (
            self.OPENAI_API_KEY or
            os.environ.get("OPENAI_API_KEY", "") or
            os.environ.get("OPENAI_KEY", "")
        ).strip()

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
