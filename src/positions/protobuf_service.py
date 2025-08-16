from datetime import datetime
from meshtastic.protobuf.mesh_pb2 import Position as PositionProtobuf
from google.protobuf.json_format import ParseDict
from . import schemas
import logging

logger = logging.getLogger("uvicorn.error")


def _convert_i_to_coordinate(value: int) -> float:
    """Convert integer coordinate to float degree value"""
    return value / 1e7


def _convert_coordinate_to_i(value: float) -> int:
    """Convert float degree value to integer coordinate"""
    return int(value * 1e7)


def _convert_unix_to_datetime(value: int) -> datetime:
    """Convert Unix timestamp to datetime"""
    return datetime.fromtimestamp(value)


def _convert_datetime_to_unix(value: datetime) -> int:
    """Convert datetime to Unix timestamp"""
    return int(value.timestamp())


def protobuf_to_position_model(
    proto_pos: PositionProtobuf,
) -> schemas.ProtoPositionModel:
    """
    Convert a Position protobuf message to a ProtoPositionModel.
    """
    position_data = {}

    for field, value in proto_pos.ListFields():
        field_name = field.name
        if field_name == "latitude_i":
            position_data["latitude"] = _convert_i_to_coordinate(value)
        elif field_name == "longitude_i":
            position_data["longitude"] = _convert_i_to_coordinate(value)
        elif field_name == "time":
            position_data["time"] = _convert_unix_to_datetime(value)
        elif field_name == "location_source":
            position_data[field_name] = schemas.LocSource(
                PositionProtobuf.LocSource.Name(value)
            )
        elif field_name == "altitude_source":
            position_data[field_name] = schemas.AltSource(
                PositionProtobuf.AltSource.Name(value)
            )
        else:
            position_data[field_name] = value

    logger.debug(f"Converting protobuf to model with data: {position_data}")
    return schemas.ProtoPositionModel(**position_data)


def position_model_to_protobuf(model: schemas.ProtoPositionModel) -> PositionProtobuf:
    """
    Convert a ProtoPositionModel back to a Position protobuf message.
    """
    data = model.model_dump(exclude_none=True)

    # Convert coordinates to integer format for protobuf
    if "latitude" in data:
        data["latitude_i"] = _convert_coordinate_to_i(float(data.pop("latitude")))
    if "longitude" in data:
        data["longitude_i"] = _convert_coordinate_to_i(float(data.pop("longitude")))

    # Convert datetime to Unix timestamp
    if "time" in data:
        data["time"] = _convert_datetime_to_unix(data["time"])

    # Convert enum strings back to integers for protobuf
    if "location_source" in data:
        data["location_source"] = list(schemas.LocSource).index(data["location_source"])
    if "altitude_source" in data:
        data["altitude_source"] = list(schemas.AltSource).index(data["altitude_source"])

    logger.debug(f"Converting model to protobuf with data: {data}")
    return ParseDict(data, PositionProtobuf())


def convert_position_proto_to_schema(
    proto_pos: PositionProtobuf, node_id: str
) -> schemas.PositionCreate:
    """
    Convert a Position protobuf message to a PositionCreate schema object.
    """
    position_model = protobuf_to_position_model(proto_pos)

    # Create PositionCreate with the base model data plus node_id
    position_data = position_model.model_dump()
    position_data["node_id"] = node_id

    return schemas.PositionCreate(**position_data)
