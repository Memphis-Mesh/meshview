from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import ForeignKey, BigInteger


class Base(AsyncAttrs, DeclarativeBase):
    pass

# Node
class Node(Base):
    __tablename__ = "node"
    id: Mapped[str] = mapped_column(primary_key=True)
    node_id: Mapped[int] = mapped_column(BigInteger, nullable=True, unique=True)
    long_name: Mapped[str] = mapped_column(nullable=True)
    short_name: Mapped[str] = mapped_column(nullable=True)
    hw_model: Mapped[str] = mapped_column(nullable=True)
    firmware: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(nullable=True)
    last_lat: Mapped[int] = mapped_column(BigInteger, nullable=True)
    last_long: Mapped[int] = mapped_column(BigInteger, nullable=True)
    channel: Mapped[str] = mapped_column(nullable=True)
    last_update: Mapped[datetime] = mapped_column(nullable=True)

    def to_dict(self):
        """Convert SQLAlchemy object to a dictionary, excluding last_update."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name != "last_update"  # Exclude last_update
        }

class Packet(Base):
    __tablename__ = "packet"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    portnum: Mapped[int] = mapped_column(nullable=True)
    from_node_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    from_node: Mapped["Node"] = relationship(
        primaryjoin="Packet.from_node_id == foreign(Node.node_id)", lazy="joined"
    )
    to_node_id: Mapped[int] = mapped_column(BigInteger,nullable=True)
    to_node: Mapped["Node"] = relationship(
        primaryjoin="Packet.to_node_id == foreign(Node.node_id)", lazy="joined", overlaps="from_node"
    )
    payload: Mapped[bytes] = mapped_column(nullable=True)
    import_time: Mapped[datetime] = mapped_column(nullable=True)
    channel: Mapped[str] = mapped_column(nullable=True)


class PacketSeen(Base):
    __tablename__ = "packet_seen"
    packet_id = mapped_column(ForeignKey("packet.id"), primary_key=True)
    node_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    node: Mapped["Node"] = relationship(
        lazy="joined", primaryjoin="PacketSeen.node_id == foreign(Node.node_id)", overlaps="from_node,to_node"
    )
    rx_time: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    hop_limit: Mapped[int] = mapped_column(nullable=True)
    hop_start: Mapped[int] = mapped_column(nullable=True)
    channel: Mapped[str] = mapped_column(nullable=True)
    rx_snr: Mapped[float] = mapped_column(nullable=True)
    rx_rssi: Mapped[int] = mapped_column(nullable=True)
    topic: Mapped[str] = mapped_column(nullable=True)
    import_time: Mapped[datetime] = mapped_column(nullable=True)


class Traceroute(Base):
    __tablename__ = "traceroute"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    packet_id = mapped_column(ForeignKey("packet.id"))
    packet: Mapped["Packet"] = relationship(
        primaryjoin="Traceroute.packet_id == foreign(Packet.id)", lazy="joined"
    )
    gateway_node_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    done: Mapped[bool] = mapped_column(nullable=True)
    route: Mapped[bytes] = mapped_column(nullable=True)
    import_time: Mapped[datetime] = mapped_column(nullable=True)
