from pydantic_settings import BaseSettings
from starlette.datastructures import Secret
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    BOOTSTRAP_SERVER: str
    TOPIC_ORDER_STATUS: str
    MOCK_SUPABASE: bool = True
    SUPABASE_URL: str
    SUPABASE_KEY: str

    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'
        extra = 'allow'

settings = Settings()

logger.info(f"BOOTSTRAP_SERVER: {settings.BOOTSTRAP_SERVER}")
logger.info(f"TOPIC_ORDER_STATUS: {settings.TOPIC_ORDER_STATUS}")
logger.info(f"MOCK_SUPABASE: {settings.MOCK_SUPABASE}")
logger.info(f"SUPABASE_URL: {settings.SUPABASE_URL}")
logger.info(f"SUPABASE_KEY: {settings.SUPABASE_KEY}")
