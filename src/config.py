from pydantic import AnyUrl
from pydantic_settings import BaseSettings

from src.constants import Environment


class Config(BaseSettings):
    DATABASE_URL: AnyUrl = "sqlite:///database.db"
    ENVIRONMENT: Environment = Environment.PRODUCTION

settings = Config()
