from sqlalchemy.orm import Session

from . import models, schemas


def get_positions(db: Session, node_id: int = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Position)
    if node_id is not None:
        query = query.order_by(models.Position.timestamp.desc()).filter(
            models.Position.node_id == node_id
        )
    return (
        query.order_by(models.Position.timestamp.desc()).offset(skip).limit(limit).all()
    )


def create_position(db: Session, position: schemas.PositionCreate) -> models.Position:
    """
    Create a new position record in the database.

    Args:
        db: Database session
        position: Position data to create

    Returns:
        The created position record
    """
    db_position = models.Position(
        node_id=position.node_id,
        latitude=position.latitude,
        longitude=position.longitude,
        altitude=position.altitude,
        time=position.time,
        location_source=position.location_source.value,  # Convert enum to int
        altitude_source=position.altitude_source.value,  # Convert enum to int
        timestamp=position.timestamp,
        timestamp_millis_adjust=position.timestamp_millis_adjust,
        PDOP=position.PDOP,
        HDOP=position.HDOP,
        VDOP=position.VDOP,
        gps_accuracy=position.gps_accuracy,
        ground_speed=position.ground_speed,
        ground_track=position.ground_track,
        fix_quality=position.fix_quality,
        fix_type=position.fix_type,
        sats_in_view=position.sats_in_view,
        sensor_id=position.sensor_id,
        next_update=position.next_update,
        seq_number=position.seq_number,
        precision_bits=position.precision_bits,
    )
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position

