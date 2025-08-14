from datetime import datetime
from pydantic import BaseModel, PositiveInt, Field
from pydantic_extra_types.coordinate import Latitude, Longitude


class Node(BaseModel):
    node_id: PositiveInt = Field(
        lt=2 ** (8 * 4),
        description="Node ID must be a 4 byte unsigned integer by meshtastic convention",
    )
    long_name: str = Field()
    short_name: str = Field(max_length=4)
    hw_model: str = Field()
    firmware: str = Field()
    role: str = Field()  # todo: replace this with a meshtastic enum
    last_lat: Latitude = Field()
    last_long: Longitude = Field()
    channel: str = Field()
    last_update: datetime = Field()
