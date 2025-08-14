import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiomqtt
from meshtastic.protobuf.mqtt_pb2 import ServiceEnvelope
from google.protobuf.message import DecodeError
from queue_consumer.mqtt_reader import get_topic_envelopes, decrypt

@pytest.fixture
def mock_mqtt_message():
    msg = MagicMock()
    msg.topic.value = "test/topic"
    msg.payload = b"test_payload"
    return msg

@pytest.fixture
def mock_service_envelope():
    envelope = MagicMock(spec=ServiceEnvelope)
    envelope.packet = MagicMock()
    envelope.packet.decoded = None
    envelope.packet.encrypted = b"encrypted_data"
    envelope.packet.id = 1
    setattr(envelope.packet, "from", 1234)
    return envelope

@pytest.mark.asyncio
async def test_get_topic_envelopes_successful_message():
    mock_client = AsyncMock()
    mock_msg = MagicMock()
    mock_msg.topic.value = "test/topic"
    mock_envelope = ServiceEnvelope()
    mock_envelope.packet.decoded.data = b"test_data"
    
    with patch('aiomqtt.Client', return_value=mock_client), \
         patch('meshtastic.protobuf.mqtt_pb2.ServiceEnvelope.FromString', return_value=mock_envelope):
        mock_client.__aenter__.return_value.messages = [mock_msg]
        
        async for topic, envelope in get_topic_envelopes("localhost", 1883, ["test/topic"], "user", "pass"):
            assert topic == "test/topic"
            assert envelope.packet.decoded.data == b"test_data"
            break

@pytest.mark.asyncio
async def test_get_topic_envelopes_decode_error():
    mock_client = AsyncMock()
    mock_msg = MagicMock()
    
    with patch('aiomqtt.Client', return_value=mock_client), \
         patch('meshtastic.protobuf.mqtt_pb2.ServiceEnvelope.FromString', side_effect=DecodeError()):
        mock_client.__aenter__.return_value.messages = [mock_msg]
        
        async for _ in get_topic_envelopes("localhost", 1883, ["test/topic"], "user", "pass"):
            pytest.fail("Should not yield any envelope on DecodeError")
            break

@pytest.mark.asyncio
async def test_get_topic_envelopes_mqtt_error():
    mock_client = AsyncMock()
    mock_client.__aenter__.side_effect = aiomqtt.MqttError("Test error")
    
    with patch('aiomqtt.Client', return_value=mock_client), \
         patch('asyncio.sleep', new_callable=AsyncMock):
        try:
            async for _ in get_topic_envelopes("localhost", 1883, ["test/topic"], "user", "pass"):
                break
        except StopAsyncIteration:
            pass
        
        mock_client.__aenter__.assert_called()

def test_decrypt_already_decoded():
    packet = MagicMock()
    packet.HasField.return_value = True
    
    decrypt(packet)
    
    packet.decoded.ParseFromString.assert_not_called()

def test_decrypt_successful():
    packet = MagicMock()
    packet.HasField.return_value = False
    packet.id = 1
    setattr(packet, "from", 1234)
    packet.encrypted = b"test_encrypted_data"
    
    decrypt(packet)
    
    packet.decoded.ParseFromString.assert_called_once()