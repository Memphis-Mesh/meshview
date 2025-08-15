from meshtastic.protobuf.mqtt_pb2 import ServiceEnvelope
from ..envelope_audits import service as envelope_audit_service
from ..envelope_audits import schemas as schemas
from ..database import SessionLocal


def persist_service_envelope(envelope_audit: ServiceEnvelope) -> schemas.EnvelopeAudits:
    """
    Persist an envelope audit to the database.
    """

    db = SessionLocal()
    db_envelope_audit = schemas.EnvelopeAuditsCreate(envelope=envelope_audit)
    return envelope_audit_service.create_envelope_audit(db, db_envelope_audit)
