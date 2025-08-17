from sqlalchemy.orm import Session

from . import models


def get_positions(db: Session, node_id: int = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Position)
    if node_id is not None:
        query = query.order_by(models.Position.timestamp.desc()).filter(
            models.Position.node_id == node_id
        )
    return (
        query.order_by(models.Position.timestamp.desc()).offset(skip).limit(limit).all()
    )


# def create_node(db: Session, node: schemas.Node):
#     db_node = models.Node(
#         node_id=node.node_id,
#         long_name=node.long_name,
#         short_name=node.short_name,
#         hw_model=node.hw_model,
#         firmware=node.firmware,
#         role=node.role,
#         last_lat=node.last_lat,
#         last_long=node.last_long,
#         channel=node.channel,
#         last_update=node.last_update,
#     )
#     db.add(db_node)
#     db.commit()
#     db.refresh(db_node)
#     return db_node
