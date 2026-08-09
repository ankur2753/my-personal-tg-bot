import pytest
from src.brokers.base_broker import BaseQueueBroker
from src.brokers.redis_broker import RedisBroker
from src.brokers.sqs_broker import SQSBroker
from src.models.payload import MessageEnvelope


@pytest.mark.asyncio
async def test_m1_redis_broker_contract():
    """Verify RedisBroker complies with BaseQueueBroker interface contract."""
    broker: BaseQueueBroker = RedisBroker()
    assert not await broker.is_connected()

    connected = await broker.connect()
    assert connected is True
    assert await broker.is_connected()

    envelope = MessageEnvelope(
        target_agent="job-hunt-agent",
        action="TEST_ACTION",
        user_id=123456789,
        chat_id=123456789,
        payload={"key": "value"},
        reply_topic="agent.job-hunt.responses"
    )

    msg_id = await broker.publish("agent.job-hunt.requests", envelope)
    assert msg_id == envelope.message_id

    await broker.disconnect()
    assert not await broker.is_connected()


@pytest.mark.asyncio
async def test_m1_sqs_broker_contract():
    """Verify SQSBroker complies with BaseQueueBroker interface contract."""
    broker: BaseQueueBroker = SQSBroker()
    connected = await broker.connect()
    assert connected is True

    envelope = MessageEnvelope(
        target_agent="finance-agent",
        action="TEST_ACTION",
        user_id=123456789,
        chat_id=123456789,
        payload={"amount": 100}
    )

    msg_id = await broker.publish("agent.finance.requests", envelope)
    assert msg_id == envelope.message_id

    await broker.disconnect()
    assert not await broker.is_connected()


def test_m1_message_envelope_serialization():
    """Verify MessageEnvelope JSON serialization roundtrip."""
    original = MessageEnvelope(
        target_agent="job-hunt-agent",
        action="TAILOR_RESUME",
        user_id=999,
        chat_id=999,
        payload={"job_url": "https://example.com/job/1"},
        reply_topic="agent.job-hunt.responses"
    )

    data_dict = original.to_json_dict()
    assert data_dict["target_agent"] == "job-hunt-agent"
    assert data_dict["user_id"] == 999
    assert data_dict["payload"]["job_url"] == "https://example.com/job/1"

    reconstructed = MessageEnvelope.from_json_dict(data_dict)
    assert reconstructed.message_id == original.message_id
    assert reconstructed.target_agent == original.target_agent
