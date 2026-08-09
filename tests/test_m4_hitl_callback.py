import pytest
from src.handlers.hitl_handler import HITLHandler
from src.models.payload import HITLPromptPayload


def test_m4_hitl_inline_keyboard_layout():
    """Verify HITLHandler formats Telegram inline keyboard layout."""
    prompt = HITLPromptPayload(
        question="What is your current notice period?",
        options=["15 Days", "30 Days", "60 Days", "Immediate"]
    )

    keyboard = HITLHandler.format_hitl_inline_keyboard(prompt)

    assert len(keyboard) == 2  # 2 rows of 2 buttons
    assert keyboard[0][0]["text"] == "15 Days"
    assert keyboard[0][0]["callback_data"].startswith(f"hitl:{prompt.prompt_id}:0")
    assert keyboard[1][1]["text"] == "Immediate"


def test_m4_hitl_answer_envelope_generation():
    """Verify HITLHandler generates answer reply envelope when button is tapped."""
    envelope = HITLHandler.create_answer_envelope(
        user_id=123456789,
        chat_id=123456789,
        prompt_id="hitl_abc123",
        selected_option="15 Days",
        target_agent="job-hunt-agent",
        reply_topic="agent.job-hunt.responses"
    )

    assert envelope.target_agent == "job-hunt-agent"
    assert envelope.action == "HITL_RESPONSE"
    assert envelope.payload["prompt_id"] == "hitl_abc123"
    assert envelope.payload["selected_option"] == "15 Days"
    assert envelope.reply_topic == "agent.job-hunt.responses"
