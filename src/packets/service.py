from sqlalchemy.orm import Session

from . import models, schemas


def get_packet(db: Session, id: int):
    return db.query(models.Packet).filter(models.Packet.id == id).first()

def get_packets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Packet).offset(skip).limit(limit).all()

def create_packet(db: Session, Packet: schemas.Packet):
    db_packet = models.Packet(
        from_node_id=Packet.from_node_id,
        to_node_id=Packet.to_node_id,
        channel=Packet.channel,
        packet_id=Packet.packet_id,
        rx_time=Packet.rx_time,
        rx_snr=Packet.rx_snr,
        rx_rssi=Packet.rx_rssi,
        hop_start=Packet.hop_start,
        relay_node=Packet.relay_node,
        decoded=Packet.decoded
    )
    db.add(db_packet)
    db.commit()
    db.refresh(db_packet)
    return db_packet
