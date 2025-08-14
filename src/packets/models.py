from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base

from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import BigInteger


class Base(AsyncAttrs, DeclarativeBase):
    pass

class Packet(Base):
    __tablename__ = "packets"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    from_node_id: Mapped[int] = mapped_column(BigInteger)
    to_node_id: Mapped[int] = mapped_column(BigInteger)
    channel: Mapped[int] = mapped_column()
    packet_id: Mapped[int] = mapped_column(BigInteger)
    rx_time: Mapped[datetime] = mapped_column()                                                                     
    rx_snr: Mapped[int] = mapped_column()                                                                                              
    rx_rssi: Mapped[int] = mapped_column()                                                                                         
    hop_start: Mapped[int] = mapped_column()                                                                                           
    relay_node: Mapped[int] = mapped_column()
    decoded: Mapped[bytes] = mapped_column(nullable=True)
