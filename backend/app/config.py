# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://user:password@localhost:5432/passagedb"
    GOOGLE_API_KEY: str = "your_google_api_key_here"

    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"), extra='ignore')

settings = Settings()
