from meshtastic.protobuf.mesh_pb2 import Position
from meshtastic.protobuf.mqtt_pb2 import ServiceEnvelope
from google.protobuf.message import DecodeError
import logging

from meshtastic.protobuf.portnums_pb2 import PortNum
from src.positions.protobuf_service import convert_position_proto_to_schema
from ..envelope_audits import service as envelope_audit_service
from ..envelope_audits import schemas as schemas
from ..nodes import service as node_service
from ..nodes import schemas as node_schemas
from ..database import SessionLocal
from datetime import datetime

logger = logging.getLogger("uvicorn.error")


def handle_position_packet(envelope_audit: ServiceEnvelope) -> None:
    """
    Handle a position packet from a ServiceEnvelope by converting and persisting the position data.
    """
    try:
        proto_pos = Position.FromString(envelope_audit.packet.decoded.payload)
        logger.debug(f"Raw position proto fields: {proto_pos.ListFields()}")

        node_id = getattr(envelope_audit.packet, "from")
        position = convert_position_proto_to_schema(proto_pos, node_id)
        logger.info(
            f"Created position from envelope: {position.model_dump_json(indent=2)}"
        )
    except Exception as e:
        logger.error(f"Error processing position: {e}", exc_info=True)


def parse_mqtt_message(payload: bytes, topic: str) -> ServiceEnvelope | None:
    """
    Parse MQTT message payload into a ServiceEnvelope.
    Returns None if parsing fails.
    """
    try:
        return ServiceEnvelope.FromString(payload)
    except DecodeError:
        logger.error(f"Error decoding message from topic {topic}, skipping")
        return None


def process_envelope(
    envelope: ServiceEnvelope,
) -> tuple[schemas.EnvelopeAudits, ServiceEnvelope]:
    """
    Process a ServiceEnvelope by:
    1. Decrypting the packet
    2. Processing its contents based on packet type
    3. Persisting to appropriate services
    4. Tracking node last heard status

    Returns the persisted audit record and processed envelope.
    """
    from .mqtt_reader import decrypt  # Import here to avoid circular dependency

    decrypt(envelope.packet)
    if not envelope.packet.decoded:
        return None, envelope

    db = SessionLocal()

    # Handle node tracking if FROM address exists
    if hasattr(envelope.packet, "from"):
        node = node_schemas.NodeCreate(
            node_id=getattr(envelope.packet, "from"), last_heard=datetime.utcnow()
        )
        node_service.upsert_node(db, node)
        logger.info(f"Upserted node with ID {node.node_id} last heard timestamp")

    envelope_model = schemas.ServiceEnvelopeModel(__root__=envelope)
    db_envelope_audit = schemas.EnvelopeAuditsCreate(envelope=envelope_model)

    if envelope.packet.decoded.portnum == PortNum.POSITION_APP:
        handle_position_packet(envelope)

    audit_record = envelope_audit_service.create_envelope_audit(db, db_envelope_audit)
    logger.info(f"Persisted envelope audit with ID {audit_record.id}")
    return audit_record, envelope
