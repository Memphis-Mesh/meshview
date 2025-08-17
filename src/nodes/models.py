from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import BigInteger, Integer

from ..models import ModelBase


class Node(ModelBase):
    __tablename__ = "nodes"
    node_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True
    )
    long_name: Mapped[str] = mapped_column(nullable=True)
    short_name: Mapped[str] = mapped_column(nullable=True)
    hw_model: Mapped[str] = mapped_column(nullable=True)
    firmware: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(nullable=True)
    channel: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_heard: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    positions: Mapped[list["Position"]] = relationship(
        "Position", back_populates="owner"
    )
