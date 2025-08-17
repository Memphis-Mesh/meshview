from sqlalchemy.orm import Session

from . import models, schemas


def get_node(db: Session, node_id: int):
    return db.query(models.Node).filter(models.Node.node_id == node_id).first()


def get_nodes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Node).offset(skip).limit(limit).all()


def create_node(db: Session, node: schemas.Node):
    db_node = models.Node(node_id=node.node_id, last_heard=node.last_heard)
    # Only set optional fields if they have values
    if node.long_name is not None:
        db_node.long_name = node.long_name
    if node.short_name is not None:
        db_node.short_name = node.short_name
    if node.hw_model is not None:
        db_node.hw_model = node.hw_model
    if node.firmware is not None:
        db_node.firmware = node.firmware
    if node.role is not None:
        db_node.role = node.role
    if node.channel is not None:
        db_node.channel = node.channel

    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node


def upsert_node(db: Session, node: schemas.Node):
    """
    Create a new node or update existing node if one exists with the same node_id.
    Only updates fields that are provided in the node schema.

    Args:
        db: Database session
        node: Node schema containing the data to upsert

    Returns:
        The created or updated node
    """
    db_node = get_node(db, node.node_id)

    if db_node:
        # Update existing node, only set fields that are provided
        data = node.model_dump(exclude_unset=True)
        for key, value in data.items():
            if value is not None:  # Only update non-None values
                setattr(db_node, key, value)
    else:
        # Create new node with required fields
        db_node = models.Node(node_id=node.node_id, last_heard=node.last_heard)
        # Set optional fields if they exist
        if node.long_name is not None:
            db_node.long_name = node.long_name
        if node.short_name is not None:
            db_node.short_name = node.short_name
        if node.hw_model is not None:
            db_node.hw_model = node.hw_model
        if node.firmware is not None:
            db_node.firmware = node.firmware
        if node.role is not None:
            db_node.role = node.role
        if node.channel is not None:
            db_node.channel = node.channel

        db.add(db_node)

    db.commit()
    db.refresh(db_node)
    return db_node
