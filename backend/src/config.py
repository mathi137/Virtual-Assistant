import  logging
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+aiomysql://appuser:password@mysql:3306/fastapi"

    LOGGING_LEVEL: str = logging.INFO
    API_PREFIX: str = "/api/v1"

settings = Settings()

logging.basicConfig(
    level=settings.LOGGING_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
