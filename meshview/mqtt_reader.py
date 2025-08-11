import base64
import asyncio
import random
import aiomqtt
from google.protobuf.message import DecodeError
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from meshtastic.protobuf.mqtt_pb2 import ServiceEnvelope

KEY = base64.b64decode("1PG7OiApB1nwvP+rz05pAQ==")


def decrypt(packet):
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


async def get_topic_envelopes(mqtt_server, mqtt_port, topics, mqtt_user, mqtt_passwd):
    identifier = str(random.getrandbits(16))
    while True:
        try:
            async with aiomqtt.Client(
                mqtt_server,
                port=mqtt_port,
                username=mqtt_user,
                password=mqtt_passwd,
                identifier=identifier,
            ) as client:
                for topic in topics:
                    print(f"Subscribing to: {topic}")
                    await client.subscribe(topic)

                async for msg in client.messages:
                    try:
                        envelope = ServiceEnvelope.FromString(msg.payload)
                    except DecodeError:
                        continue

                    decrypt(envelope.packet)
                    # print(envelope.packet.decoded)
                    if not envelope.packet.decoded:
                        continue

                    # Skip packets from specific node
                    if getattr(envelope.packet, "from", None) == 2144342101:
                        continue

                    yield msg.topic.value, envelope

        except aiomqtt.MqttError as e:
            print(f"MQTT error: {e}, reconnecting in 1s...")
            await asyncio.sleep(1)
