from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic_extra_types.coordinate import Latitude, Longitude


class LocSource(str, Enum):
    """Location source types"""
    LOC_UNSET = "LOC_UNSET"
    LOC_MANUAL = "LOC_MANUAL" 
    LOC_INTERNAL = "LOC_INTERNAL"
    LOC_EXTERNAL = "LOC_EXTERNAL"


class AltSource(str, Enum):
    """Altitude source types"""
    ALT_UNSET = "ALT_UNSET"
    ALT_MANUAL = "ALT_MANUAL"
    ALT_INTERNAL = "ALT_INTERNAL"
    ALT_EXTERNAL = "ALT_EXTERNAL"
    ALT_BAROMETRIC = "ALT_BAROMETRIC"


class ProtoPositionModel(BaseModel):
    """Base position model"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    latitude: Optional[Latitude] = Field(None)
    longitude: Optional[Longitude] = Field(None)
    altitude: Optional[int] = Field(None)
    time: Optional[datetime] = Field(None)
    location_source: LocSource = Field(default=LocSource.LOC_UNSET)
    altitude_source: AltSource = Field(default=AltSource.ALT_UNSET)
    timestamp: int = Field(default=0)
    timestamp_millis_adjust: int = Field(default=0)
    PDOP: int = Field(default=0)
    HDOP: int = Field(default=0)
    VDOP: int = Field(default=0)
    gps_accuracy: int = Field(default=0)
    ground_speed: Optional[int] = Field(None)
    ground_track: Optional[int] = Field(None)
    fix_quality: int = Field(default=0)
    fix_type: int = Field(default=0)
    sats_in_view: int = Field(default=0)
    sensor_id: int = Field(default=0)
    next_update: int = Field(default=0)
    seq_number: int = Field(default=0)
    precision_bits: int = Field(default=0)

# Base model for database operations
class PositionBase(ProtoPositionModel):
    """Base model for Position with added database fields"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    node_id: int = Field(description="ID of the node that reported this position")


class PositionCreate(PositionBase):
    """Schema for creating a new position record (before database insertion)"""
    pass


class Position(PositionBase):
    """Schema for position records after database insertion"""
    id: int = Field(description="Database record ID")
