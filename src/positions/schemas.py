from datetime import datetime
from enum import Enum
import logging
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from google.protobuf.json_format import MessageToDict, ParseDict
from meshtastic.protobuf.mesh_pb2 import Position


# Configure logger at module level
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class LocSource(str, Enum):
    """Maps to Position.LocSource in protobuf"""
    LOC_UNSET = "LOC_UNSET"
    LOC_MANUAL = "LOC_MANUAL" 
    LOC_INTERNAL = "LOC_INTERNAL"
    LOC_EXTERNAL = "LOC_EXTERNAL"


class AltSource(str, Enum):
    """Maps to Position.AltSource in protobuf"""
    ALT_UNSET = "ALT_UNSET"
    ALT_MANUAL = "ALT_MANUAL"
    ALT_INTERNAL = "ALT_INTERNAL"
    ALT_EXTERNAL = "ALT_EXTERNAL"
    ALT_BAROMETRIC = "ALT_BAROMETRIC"


class ProtoPositionModel(BaseModel):
    """Wrapper for Position that handles protobuf serialization"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    latitude_i: Optional[int] = Field(
        None,
        description="Latitude multiplied by 1e-7 to get degrees in floating point"
    )
    longitude_i: Optional[int] = Field(
        None,
        description="Longitude multiplied by 1e-7 to get degrees in floating point"
    )
    altitude: Optional[int] = Field(
        None,
        description="Altitude in meters above MSL"
    )
    time: int = Field(
        default=0,
        description="Seconds since 1970"
    )
    location_source: LocSource = Field(
        default=LocSource.LOC_UNSET,
        description="Source of location data"
    )
    altitude_source: AltSource = Field(
        default=AltSource.ALT_UNSET,
        description="Source of altitude data"
    )
    timestamp: int = Field(
        default=0,
        description="Positional timestamp in integer epoch seconds"
    )
    timestamp_millis_adjust: int = Field(
        default=0,
        description="Milliseconds adjustment for timestamp"
    )
    PDOP: int = Field(
        default=0,
        description="Position dilution of precision in 1/100 units"
    )
    HDOP: int = Field(
        default=0,
        description="Horizontal dilution of precision in 1/100 units"
    )
    VDOP: int = Field(
        default=0,
        description="Vertical dilution of precision in 1/100 units"
    )
    gps_accuracy: int = Field(
        default=0,
        description="GPS accuracy in millimeters"
    )
    ground_speed: Optional[int] = Field(
        None,
        description="Ground speed in meters per second"
    )
    ground_track: Optional[int] = Field(
        None,
        description="True North track in 1/100 degrees"
    )
    fix_quality: int = Field(
        default=0,
        description="GPS fix quality"
    )
    fix_type: int = Field(
        default=0,
        description="GPS fix type 2D/3D"
    )
    sats_in_view: int = Field(
        default=0,
        description="Number of satellites in view"
    )
    sensor_id: int = Field(
        default=0,
        description="ID for multiple positioning sensors"
    )
    next_update: int = Field(
        default=0,
        description="Expected seconds until next update"
    )
    seq_number: int = Field(
        default=0,
        description="Sequence number for detecting lost updates"
    )
    precision_bits: int = Field(
        default=0,
        description="Bits of precision set by sending node"
    )

    def __init__(self, **data: Any):
        logger.debug(f"Initializing ProtoPositionModel with data: {data}")
        root_data = data.get("__root__")
        
        # Prepare converted data with node_id and other non-proto fields
        converted_data = {k: v for k, v in data.items() if k != "__root__"}
        
        if isinstance(root_data, Position):
            # Direct protobuf object
            logger.debug("Processing direct protobuf Position object")
            proto_pos = root_data
            # Map protobuf fields to model fields
            for field, value in proto_pos.ListFields():
                field_name = field.name
                try:
                    if field_name == "location_source":
                        enum_value = LocSource._member_names_[value]
                        logger.debug(f"Converting location_source enum {value} to {enum_value}")
                        converted_data[field_name] = enum_value
                    elif field_name == "altitude_source":
                        enum_value = AltSource._member_names_[value]
                        logger.debug(f"Converting altitude_source enum {value} to {enum_value}")
                        converted_data[field_name] = enum_value
                    else:
                        converted_data[field_name] = value
                    logger.debug(f"Set field {field_name} = {converted_data[field_name]}")
                except Exception as e:
                    logger.error(f"Error converting field {field_name}: {e}", exc_info=True)
        else:
            logger.debug("Initializing with non-protobuf data")
            super().__init__(**data)
            return

        logger.debug(f"Final converted data: {converted_data}")
        super().__init__(**converted_data)

    def to_protobuf(self) -> Position:
        """Convert back to protobuf message"""
        data = self.model_dump(exclude_none=True)
        # Convert enum strings back to integers for protobuf
        if "location_source" in data:
            data["location_source"] = list(LocSource).index(LocSource(data["location_source"]))
        if "altitude_source" in data:
            data["altitude_source"] = list(AltSource).index(AltSource(data["altitude_source"]))
        
        logger.debug(f"Converting to protobuf: {data}")
        return ParseDict(data, Position())


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
