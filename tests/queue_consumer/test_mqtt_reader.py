import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from meshtastic.protobuf.mqtt_pb2 import ServiceEnvelope
from meshtastic.protobuf.mesh_pb2 import MeshPacket, Data
from src.queue_consumer.mqtt_reader import (
    create_mqtt_client,
    subscribe_to_topics,
    get_topic_envelopes,
    decrypt,
)


@pytest.fixture
def mock_mqtt_client():
    client = AsyncMock()
    client.subscribe = AsyncMock()
    client.messages = AsyncMock()
    return client


@pytest.fixture
def sample_service_envelope():
    packet = MeshPacket()
    packet.id = 123
    # The 'from' field is accessed using array notation since it's a reserved word
    setattr(packet, "from", 456)
    packet.decoded.data.payload = b"test message"

    envelope = ServiceEnvelope()
    envelope.packet.CopyFrom(packet)
    return envelope


@pytest.mark.asyncio
async def test_create_mqtt_client():
    with patch("src.queue_consumer.mqtt_reader.aiomqtt.Client") as mock_client:
        await create_mqtt_client("localhost", 1883, "user", "pass", "test-id")
        mock_client.assert_called_once_with(
            "localhost",
            port=1883,
            username="user",
            password="pass",
            identifier="test-id",
        )


@pytest.mark.asyncio
async def test_subscribe_to_topics(mock_mqtt_client):
    topics = ["topic1", "topic2"]
    await subscribe_to_topics(mock_mqtt_client, topics)

    assert mock_mqtt_client.subscribe.call_count == 2
    mock_mqtt_client.subscribe.assert_any_call("topic1")
    mock_mqtt_client.subscribe.assert_any_call("topic2")


def test_decrypt_already_decoded():
    packet = MeshPacket()
    # Properly initialize the decoded.data field
    packet.decoded.MergeFrom(Data(payload=b"already decoded"))
    decrypt(packet)
    assert packet.decoded.payload == b"already decoded"


@pytest.mark.asyncio
async def test_get_topic_envelopes_success():
    mock_client = AsyncMock()
    mock_msg = MagicMock()
    mock_msg.topic.value = "test/topic"
    mock_msg.payload = ServiceEnvelope().SerializeToString()

    # Create a proper async iterator
    class AsyncIterator:
        def __init__(self, messages):
            self.messages = messages

        def __aiter__(self):
            return self

        async def __anext__(self):
            if not self.messages:
                raise StopAsyncIteration
            return self.messages.pop(0)

    mock_client.messages = AsyncIterator([mock_msg])
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch(
        "src.queue_consumer.mqtt_reader.create_mqtt_client", return_value=mock_client
    ):
        gen = get_topic_envelopes("localhost", 1883, ["test/topic"], None, None)
        topic, envelope = await anext(gen)
        assert topic == "test/topic"
        assert isinstance(envelope, ServiceEnvelope)


@pytest.mark.asyncio
async def test_get_topic_envelopes_reconnect():
    mock_client = AsyncMock()

    # Create a proper async iterator that raises an exception
    class FailingAsyncIterator:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise Exception("Connection lost")

    mock_client.messages = FailingAsyncIterator()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with (
        patch(
            "src.queue_consumer.mqtt_reader.create_mqtt_client",
            return_value=mock_client,
        ),
        patch("asyncio.sleep", return_value=None),
    ):
        gen = get_topic_envelopes("localhost", 1883, ["test/topic"], None, None)
        with pytest.raises(Exception, match="Connection lost"):
            await anext(gen)
