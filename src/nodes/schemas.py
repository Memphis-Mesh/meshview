from pydantic import BaseModel, PositiveInt, PastDatetime
from pydantic_extra_types.coordinate import Latitude, Longitude
from pydantic_extra_types.semantic_version import SemanticVersion


from sqlmodel import Field, SQLModel


class Node(BaseModel):
    node_id: PositiveInt = Field(lt=2**(8*4), description="Node ID must be a 4 byte unsigned integer by meshtastic convention")
    long_name: str = Field()
    short_name: str = Field(max_length=4)
    hw_model: str = Field()
    firmware: SemanticVersion = Field()
    role: str = Field() # todo: replace this with a meshtastic enum
    last_lat: Latitude = Field()
    last_long: Longitude = Field()
    channel: str = Field()
    last_update: PastDatetime = Field()



class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)


class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class HeroCreate(HeroBase):
    pass


class HeroPublic(HeroBase):
    id: int


class HeroUpdate(SQLModel):
    name: str | None = None
    secret_name: str | None = None
    age: int | None = None

