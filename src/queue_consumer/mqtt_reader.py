import base64
import asyncio
import logging
import random
import aiomqtt
from google.protobuf.message import DecodeError
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from meshtastic.protobuf.mesh_pb2 import MeshPacket
from meshtastic.protobuf.mqtt_pb2 import ServiceEnvelope
from .service import persist_service_envelope

# TODO: move this to a config value, ideally tied to the channel
KEY = base64.b64decode("1PG7OiApB1nwvP+rz05pAQ==")

logger = logging.getLogger("uvicorn.error")


def decrypt(packet: MeshPacket) -> MeshPacket:
    if packet.HasField("decoded"):
        return
    packet_id = packet.id.to_bytes(8, "little")
    from_node_id = getattr(packet, "from").to_bytes(8, "little")
    nonce = packet_id + from_node_id

    cipher = Cipher(algorithms.AES(KEY), modes.CTR(nonce))
    decryptor = cipher.decryptor()
    raw_proto = decryptor.update(packet.encrypted) + decryptor.finalize()
    try:
        packet.decoded.ParseFromString(raw_proto)
    except DecodeError:
        pass


async def create_mqtt_client(
    mqtt_server: str,
    mqtt_port: int,
    mqtt_user: str | None,
    mqtt_passwd: str | None,
    identifier: str,
) -> aiomqtt.Client:
    """Create and return a configured MQTT client."""
    return aiomqtt.Client(
        mqtt_server,
        port=mqtt_port,
        username=mqtt_user,
        password=mqtt_passwd,
        identifier=identifier,
    )


async def subscribe_to_topics(client: aiomqtt.Client, topics: list[str]) -> None:
    """Subscribe to the given list of topics."""
    for topic in topics:
        logger.info(f"Subscribing to MQTT topic {topic}")
        await client.subscribe(topic)


async def get_topic_envelopes(
    mqtt_server: str,
    mqtt_port: int,
    topics: list[str],
    mqtt_user: str | None,
    mqtt_passwd: str | None,
):
    """
    Connect to MQTT broker and yield processed messages from subscribed topics.
    Handles reconnection on errors.
    """
    identifier = str(random.getrandbits(16))

    while True:
        try:
            async with await create_mqtt_client(
                mqtt_server, mqtt_port, mqtt_user, mqtt_passwd, identifier
            ) as client:
                await subscribe_to_topics(client, topics)

                async for msg in client.messages:
                    envelope = ServiceEnvelope.FromString(msg.payload)
                    if not envelope:
                        continue

                    decrypt(envelope.packet)
                    if not envelope.packet.decoded:
                        continue
                    # TODO: bring this featuer back but with a specific configurable disallow list
                    # # Skip packets from specific node
                    # if getattr(envelope.packet, "from", None) == 2144342101:
                    #     continue

                    logger.info(
                        f"From MQTT topic {msg.topic.value}, received envelope: {envelope}"
                    )
                    db_envelope_audit = persist_service_envelope(envelope)
                    logger.info(
                        f"Persisted envelope audit with ID {db_envelope_audit.id}"
                    )
                    yield msg.topic.value, envelope

        except aiomqtt.MqttError as e:
            logger.error(f"MQTT error: {e}, reconnecting in 1s...")
            await asyncio.sleep(1)
