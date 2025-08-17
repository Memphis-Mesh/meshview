from fastapi import FastAPI
import logging

from .models import ModelBase

from .nodes import router as NodesRouter
from .envelope_audits import router as EnvelopeAuditsRouter
from .positions import router as PositionsRouter
from .database import engine
from .queue_consumer import mqtt_reader
import asyncio
from .config import settings


# Configure root logger
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Configure specific loggers
logging.getLogger("src.positions.schemas").setLevel(logging.DEBUG)


def create_db_and_tables():
    ModelBase.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(NodesRouter.router)
app.include_router(PositionsRouter.router)
app.include_router(EnvelopeAuditsRouter.router)
app.include_router(PositionsRouter.router)


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
