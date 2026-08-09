import pytest
from src.config import Settings
from src.brokers.redis_broker import RedisBroker
from src.handlers.router import IntentRouter


@pytest.fixture
def settings():
    return Settings(
        allowed_telegram_user_ids=[123456789],
        topic_job_hunt_requests="agent.job-hunt.requests",
        topic_finance_requests="agent.finance.requests"
    )


@pytest.fixture
def router(settings):
    broker = RedisBroker()
    return IntentRouter(broker=broker, settings=settings)


def test_m2_security_guard_whitelist(settings):
    """Verify unauthorized users are blocked by security guard."""
    assert settings.is_user_allowed(123456789) is True
    assert settings.is_user_allowed(999999999) is False


def test_m2_intent_detection(router):
    """Verify intent classifier correctly categorizes message input."""
    assert router.detect_intent("https://linkedin.com/jobs/view/12345") == "job-hunt"
    assert router.detect_intent("/job tailor resume for python dev") == "job-hunt"
    assert router.detect_intent("/expense 1500 groceries") == "finance"
    assert router.detect_intent("/hitl respond 15 days") == "hitl"
    assert router.detect_intent("Hello, how are you?") == "default"


@pytest.mark.asyncio
async def test_m2_message_routing_allowed_user(router):
    """Verify router publishes message for authorized user."""
    await router.broker.connect()

    envelope = await router.route_message(
        text="https://naukri.com/job-listings-python-dev",
        user_id=123456789,
        chat_id=123456789
    )

    assert envelope is not None
    assert envelope.target_agent == "job-hunt-agent"
    assert envelope.action == "TAILOR_RESUME"
    assert envelope.reply_topic == "agent.job-hunt.responses"

    await router.broker.disconnect()


@pytest.mark.asyncio
async def test_m2_message_routing_unauthorized_user(router):
    """Verify router raises PermissionError for unauthorized user."""
    with pytest.raises(PermissionError):
        await router.route_message(
            text="/job test",
            user_id=999999999,
            chat_id=999999999
        )
