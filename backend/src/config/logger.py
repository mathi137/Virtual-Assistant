import  logging

from src.config.settings import settings

logging.getLogger('passlib').setLevel(logging.ERROR)
logging.getLogger('passlib.handlers.bcrypt').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.engine.Engine').setLevel(logging.WARNING)
logging.getLogger('aiomysql').setLevel(logging.ERROR)
logging.getLogger('aiomysql.cursors').setLevel(logging.ERROR)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)


logging.basicConfig(
    level=settings.LOGGING_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
