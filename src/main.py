from fastapi import Depends, FastAPI

from .nodes import router as NodesRouter
from .nodes import models as NodeModels
from .database import engine
from .queue_consumer import mqtt_reader
from typing import Annotated
from sqlalchemy.orm import Session
import logging
import asyncio
from .config import settings

def create_db_and_tables():
    NodeModels.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(NodesRouter.router)

async def consume_messages():
    async for topic, env in mqtt_reader.get_topic_envelopes(
        settings.MQTT.server, settings.MQTT.port, settings.MQTT.topics, settings.MQTT.username, settings.MQTT.password
    ):
        continue

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    asyncio.create_task(consume_messages())

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
