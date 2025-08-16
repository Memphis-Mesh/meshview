from meshtastic.protobuf.mesh_pb2 import Position
from meshtastic.protobuf.mqtt_pb2 import ServiceEnvelope
from google.protobuf.message import DecodeError
import logging

from meshtastic.protobuf.portnums_pb2 import PortNum
from src.positions.protobuf_service import convert_position_proto_to_schema
from ..envelope_audits import service as envelope_audit_service
from ..envelope_audits import schemas as schemas
from ..database import SessionLocal

logger = logging.getLogger("uvicorn.error")


def persist_service_envelope(envelope_audit: ServiceEnvelope) -> schemas.EnvelopeAudits:
    """
    Persist an MQTT ServiceEnvelope to the database in it's EnvelopeAudits format.
    """
    db = SessionLocal()
    envelope_model = schemas.ServiceEnvelopeModel(__root__=envelope_audit)
    db_envelope_audit = schemas.EnvelopeAuditsCreate(envelope=envelope_model)

    if (
        envelope_audit.packet.HasField("decoded")
        and envelope_audit.packet.decoded.portnum == PortNum.POSITION_APP
    ):
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

    return envelope_audit_service.create_envelope_audit(db, db_envelope_audit)


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
    Process a ServiceEnvelope by decrypting it and persisting to database.
    Returns the persisted audit record and processed envelope.
    """
    from .mqtt_reader import decrypt  # Import here to avoid circular dependency

    decrypt(envelope.packet)
    if not envelope.packet.decoded:
        return None

    db_envelope_audit = persist_service_envelope(envelope)
    logger.info(f"Persisted envelope audit with ID {db_envelope_audit.id}")
    return db_envelope_audit, envelope
