import  logging
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 30

    LOGGING_LEVEL: str = logging.INFO
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "mysql+aiomysql://appuser:password@mysql:3306/fastapi"

    OPENAI_API_KEY: str

settings = Settings()

logging.basicConfig(
    level=settings.LOGGING_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.getLogger('passlib').setLevel(logging.ERROR)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
