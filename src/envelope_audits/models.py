from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import BigInteger, Integer, DateTime, PickleType
from ..models import ModelBase


class EnvelopeAudits(ModelBase):
    __tablename__ = "envelope_audits"
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    envelope: Mapped[bytes] = mapped_column(PickleType)
