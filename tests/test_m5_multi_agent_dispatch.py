import pytest
from src.config import Settings
from src.brokers.redis_broker import RedisBroker
from src.handlers.router import IntentRouter


@pytest.mark.asyncio
async def test_m5_multi_agent_concurrent_routing():
    """Verify router can route messages to distinct agent queues without crosstalk."""
    settings = Settings(allowed_telegram_user_ids=[123456789])
    broker = RedisBroker()
    await broker.connect()

    router = IntentRouter(broker=broker, settings=settings)

    # Route job agent message
    job_envelope = await router.route_message(
        text="/job apply https://company.com/job/1",
        user_id=123456789,
        chat_id=123456789
    )

    # Route finance agent message
    fin_envelope = await router.route_message(
        text="/expense 500 grocery shopping",
        user_id=123456789,
        chat_id=123456789
    )

    assert job_envelope.target_agent == "job-hunt-agent"
    assert fin_envelope.target_agent == "finance-agent"

    assert "agent.job-hunt.requests" in broker._published_messages
    assert "agent.finance.requests" in broker._published_messages

    assert len(broker._published_messages["agent.job-hunt.requests"]) == 1
    assert len(broker._published_messages["agent.finance.requests"]) == 1

    await broker.disconnect()
