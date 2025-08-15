from meshtastic.protobuf.mqtt_pb2 import ServiceEnvelope
from google.protobuf.message import DecodeError
import logging
from ..envelope_audits import service as envelope_audit_service
from ..envelope_audits import schemas as schemas
from ..database import SessionLocal

logger = logging.getLogger("uvicorn.error")


def persist_service_envelope(envelope_audit: ServiceEnvelope) -> schemas.EnvelopeAudits:
    """
    Persist an MQTT ServiceEnvelope to the database in it's EnvelopeAudits format.
    """

    db = SessionLocal()
    # Wrap the ServiceEnvelope in a ServiceEnvelopeModel using __root__
    envelope_model = schemas.ServiceEnvelopeModel(__root__=envelope_audit)
    db_envelope_audit = schemas.EnvelopeAuditsCreate(envelope=envelope_model)
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
