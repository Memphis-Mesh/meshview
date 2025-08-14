from pydantic import AnyUrl, BaseModel
from pydantic_settings import BaseSettings

from src.constants import Environment


class MQTTSettings(BaseModel):
    server: str = "mqtt.meshtastic.org"
    port: int = 1883
    username: str = "meshdev"
    password: str = "large4cats"
    topics: list[str] = ["msh/US/memphisme.sh/#"]


class Config(BaseSettings):
    DATABASE_URL: AnyUrl = "sqlite:///database.db"
    ENVIRONMENT: Environment = Environment.PRODUCTION
    MQTT: MQTTSettings = MQTTSettings()


settings = Config()
