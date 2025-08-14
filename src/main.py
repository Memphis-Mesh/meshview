from fastapi import FastAPI

from .models import ModelBase

from .nodes import router as NodesRouter
from .database import engine
from .queue_consumer import mqtt_reader
import asyncio
from .config import settings


def create_db_and_tables():
    ModelBase.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(NodesRouter.router)


async def consume_messages() -> None:
    async for topic, env in mqtt_reader.get_topic_envelopes(
        settings.MQTT.server,
        settings.MQTT.port,
        settings.MQTT.topics,
        settings.MQTT.username,
        settings.MQTT.password,
    ):
        # TODO: make this do something
        continue


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    asyncio.create_task(consume_messages())


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
