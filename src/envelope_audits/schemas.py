from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from google.protobuf.json_format import MessageToDict, ParseDict
from meshtastic.protobuf.mqtt_pb2 import ServiceEnvelope


class ChannelEnum(str, Enum):
    """Meshtastic channel types"""
    UNKNOWN = "UNKNOWN"
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    LONGFAST = "LongFast"
    LONGSLOW = "LongSlow"
    SHORT = "ShortSlow"


class ProtoEnvelopeModel(BaseModel):
    """Wrapper for ServiceEnvelope that handles protobuf serialization"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str = Field(default="")
    gateway_id: str = Field(default="")
    channel_id: Optional[ChannelEnum] = Field(default=None)
    packet: dict = Field(default_factory=dict)
    
    def __init__(self, **data: Any):
        if isinstance(data.get('__root__'), ServiceEnvelope):
            # Convert protobuf message to dict
            data = MessageToDict(
                data['__root__'],
                preserving_proto_field_name=True
            )
        # Handle packet conversion for both direct packet objects and string representations
        if 'packet' in data:
            if hasattr(data['packet'], 'DESCRIPTOR'):  # It's a protobuf message
                data['packet'] = MessageToDict(
                    data['packet'],
                    preserving_proto_field_name=True
                )
            elif isinstance(data['packet'], str):
                data['packet'] = {'raw': data['packet']}
        super().__init__(**data)

    @field_validator('packet', mode='before')
    @classmethod
    def convert_packet_to_dict(cls, v):
        if hasattr(v, 'DESCRIPTOR'):  # It's a protobuf message
            return MessageToDict(
                v,
                preserving_proto_field_name=True
            )
        if isinstance(v, str):
            return {'raw': v}
        return v

    def to_protobuf(self) -> ServiceEnvelope:
        """Convert back to protobuf message"""
        return ParseDict(self.model_dump(), ServiceEnvelope())


# Remove the dynamic model creation since we're explicitly defining fields
ServiceEnvelopeModel = ProtoEnvelopeModel

class EnvelopeAuditsBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    envelope: ServiceEnvelopeModel = Field(default_factory=ServiceEnvelopeModel)


class EnvelopeAuditsCreate(EnvelopeAuditsBase):
    pass


class EnvelopeAudits(EnvelopeAuditsBase):
    id: int = Field()
    created_at: datetime = Field()
