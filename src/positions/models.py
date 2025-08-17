from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import BigInteger, Integer, ForeignKey, Float, DateTime
from typing import Optional
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

    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    altitude: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    location_source: Mapped[int] = mapped_column(Integer, default=0)  # For LocSource enum
    altitude_source: Mapped[int] = mapped_column(Integer, default=0)  # For AltSource enum
    timestamp: Mapped[int] = mapped_column(Integer, default=0)
    timestamp_millis_adjust: Mapped[int] = mapped_column(Integer, default=0)
    PDOP: Mapped[int] = mapped_column(Integer, default=0)
    HDOP: Mapped[int] = mapped_column(Integer, default=0)
    VDOP: Mapped[int] = mapped_column(Integer, default=0)
    gps_accuracy: Mapped[int] = mapped_column(Integer, default=0)
    ground_speed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ground_track: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fix_quality: Mapped[int] = mapped_column(Integer, default=0)
    fix_type: Mapped[int] = mapped_column(Integer, default=0)
    sats_in_view: Mapped[int] = mapped_column(Integer, default=0)
    sensor_id: Mapped[int] = mapped_column(Integer, default=0)
    next_update: Mapped[int] = mapped_column(Integer, default=0)
    seq_number: Mapped[int] = mapped_column(Integer, default=0)
    precision_bits: Mapped[int] = mapped_column(Integer, default=0)
