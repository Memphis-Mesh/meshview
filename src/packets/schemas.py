from datetime import datetime
from pydantic import BaseModel, Field


class Packet(BaseModel):
    id: int = Field()
    from_node_id: int = Field()
    to_node_id: int = Field()
    channel: int = Field()
    packet_id: int = Field()
    rx_time: datetime = Field()                                                                     
    rx_snr: int = Field()                                                                                              
    rx_rssi: int = Field()                                                                                         
    hop_start: int = Field()                                                                                           
    relay_node: int = Field()
    decoded: bytes = Field()
