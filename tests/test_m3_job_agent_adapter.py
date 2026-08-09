import pytest
from src.brokers.redis_broker import RedisBroker
from src.handlers.job_agent_handler import JobAgentHandler
from src.models.payload import JobHuntPayload, JobHuntResponsePayload, MessageEnvelope


def test_m3_job_agent_request_envelope_creation():
    """Verify JobAgentHandler constructs valid request envelope."""
    broker = RedisBroker()
    handler = JobAgentHandler(broker=broker)

    payload = JobHuntPayload(
        job_url="https://company.com/careers/python-lead",
        custom_notes="Focus on Playwright and Docker",
        action_type="TAILOR_RESUME"
    )

    envelope = handler.create_request_envelope(user_id=123, chat_id=123, job_payload=payload)

    assert envelope.target_agent == "job-hunt-agent"
    assert envelope.action == "TAILOR_RESUME"
    assert envelope.payload["job_url"] == "https://company.com/careers/python-lead"
    assert envelope.payload["custom_notes"] == "Focus on Playwright and Docker"


def test_m3_job_agent_response_envelope_parsing():
    """Verify JobAgentHandler parses response envelope correctly."""
    broker = RedisBroker()
    handler = JobAgentHandler(broker=broker)

    response_env = MessageEnvelope(
        target_agent="my-personal-tg-bot",
        action="JOB_HUNT_RESPONSE",
        user_id=123,
        chat_id=123,
        payload={
            "status": "SUCCESS",
            "pdf_path": "/path/to/tailored_resume.pdf",
            "png_preview_path": "/path/to/resume_preview.png",
            "ats_score": 88.5
        }
    )

    parsed = handler.parse_response_envelope(response_env)

    assert parsed.status == "SUCCESS"
    assert parsed.pdf_path == "/path/to/tailored_resume.pdf"
    assert parsed.png_preview_path == "/path/to/resume_preview.png"
    assert parsed.ats_score == 88.5
