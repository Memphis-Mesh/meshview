from datetime import datetime
from typing import Optional
from pydantic import BaseModel, PositiveInt, Field

from ..positions.schemas import Position


class NodeBase(BaseModel):
    node_id: PositiveInt = Field(
        lt=2 ** (8 * 4),
        description="Node ID must be a 4 byte unsigned integer by meshtastic convention",
    )
    long_name: Optional[str] = None
    short_name: Optional[str] = None
    hw_model: Optional[str] = None
    firmware: Optional[str] = None
    role: Optional[str] = None
    channel: Optional[str] = None
    last_heard: datetime


class NodeCreate(NodeBase):
    pass


class Node(NodeBase):
    positions: list[Position] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # newer pydantic v2 syntax instead of orm_mode
