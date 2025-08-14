from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from meshtastic.protobuf.mqtt_pb2 import ServiceEnvelope


class EnvelopeAuditsBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    envelope: ServiceEnvelope = Field()


class EvenlopeAuditsCreate(EnvelopeAuditsBase):
    pass


class EnvelopeAudits(EnvelopeAuditsBase):
    id: int = Field()
    created_at: datetime = Field()
