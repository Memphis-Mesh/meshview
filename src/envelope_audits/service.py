import pickle
from sqlalchemy.orm import Session

from . import models, schemas


def get_envelope_audit(db: Session, id: int):
    # TODO: handle unpickling envelope
    return db.query(models.EnvelopeAudits).filter(models.EnvelopeAudits.id == id).first()


def get_envelope_aduits(db: Session, skip: int = 0, limit: int = 100):
    # TODO: handle unpickling envelope
    return db.query(models.EnvelopeAudits).offset(skip).limit(limit).all()


def create_envelope_audit(db: Session, envelope_audit: schemas.EvenlopeAuditsCreate):
    db_envelope_audit = models.EnvelopeAudits(
        envelope=pickle.dumps(envelope_audit.envelope)
    )
    db.add(db_envelope_audit)
    db.commit()
    db.refresh(db_envelope_audit)
    return db_envelope_audit
