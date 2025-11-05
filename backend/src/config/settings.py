from pydantic_settings import BaseSettings
import logging

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 30

    LOGGING_LEVEL: str = logging.INFO
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "mysql+aiomysql://appuser:password@mysql:3306/fastapi"

    OPENAI_API_KEY: str
    
    CHATBOT_WEBHOOK_URL: str = "http://chat_bot:8001/agent/event"

settings = Settings()