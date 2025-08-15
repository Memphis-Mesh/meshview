import pytest
from unittest.mock import patch, MagicMock
from meshtastic.protobuf.mqtt_pb2 import ServiceEnvelope
from meshtastic.protobuf.mesh_pb2 import MeshPacket, Data
from src.queue_consumer.service import (
    parse_mqtt_message,
    process_envelope,
    persist_service_envelope,
)
from src.envelope_audits import schemas  # Changed from relative to absolute import


@pytest.fixture
def sample_service_envelope():
    packet = MeshPacket()
    packet.id = 123
    setattr(packet, 'from', 456)
    # Properly initialize the decoded field with Data message
    data_message = Data()
    data_message.payload = b"test message"
    packet.decoded.MergeFrom(data_message)
    
    envelope = ServiceEnvelope()
    envelope.packet.CopyFrom(packet)
    return envelope


def test_parse_mqtt_message_success(sample_service_envelope):
    payload = sample_service_envelope.SerializeToString()
    result = parse_mqtt_message(payload, "test/topic")
    assert isinstance(result, ServiceEnvelope)
    assert result.packet.id == 123


def test_parse_mqtt_message_failure():
    result = parse_mqtt_message(b"invalid data", "test/topic")
    assert result is None


@pytest.mark.asyncio
async def test_process_envelope(sample_service_envelope):
    mock_audit = MagicMock()
    
    with patch("src.queue_consumer.service.persist_service_envelope",
              return_value=mock_audit):
        result = process_envelope(sample_service_envelope)
        assert result is not None
        audit, envelope = result
        assert audit == mock_audit
        assert envelope == sample_service_envelope


def test_persist_service_envelope(sample_service_envelope):
    mock_db = MagicMock()
    mock_envelope_audit = MagicMock()
    
    with patch("src.queue_consumer.service.SessionLocal",
              return_value=mock_db), \
         patch("src.queue_consumer.service.envelope_audit_service.create_envelope_audit",
               return_value=mock_envelope_audit):
        
        result = persist_service_envelope(sample_service_envelope)
        assert result == mock_envelope_audit