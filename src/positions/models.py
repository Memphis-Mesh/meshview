from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import BigInteger, Integer, ForeignKey
from ..models import ModelBase


class Position(ModelBase):
    __tablename__ = "positions"
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    node_id: Mapped[int] = mapped_column(ForeignKey("nodes.node_id"))
    owner = relationship("Node", back_populates="positions")
