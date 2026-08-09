from typing import Dict, Any, List
from ..models.payload import HITLPromptPayload, MessageEnvelope


class HITLHandler:
    """Handler for Human-in-the-Loop interactive question prompts and answer callbacks."""

    @staticmethod
    def format_hitl_inline_keyboard(hitl_payload: HITLPromptPayload) -> List[List[Dict[str, str]]]:
        """Generate inline keyboard button array structure for Telegram API."""
        keyboard = []
        row = []
        for idx, option in enumerate(hitl_payload.options):
            row.append({
                "text": option,
                "callback_data": f"hitl:{hitl_payload.prompt_id}:{idx}"
            })
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        return keyboard

    @staticmethod
    def create_answer_envelope(
        user_id: int,
        chat_id: int,
        prompt_id: str,
        selected_option: str,
        target_agent: str,
        reply_topic: str
    ) -> MessageEnvelope:
        """Create reply envelope when candidate taps an inline button."""
        return MessageEnvelope(
            target_agent=target_agent,
            action="HITL_RESPONSE",
            user_id=user_id,
            chat_id=chat_id,
            payload={
                "prompt_id": prompt_id,
                "selected_option": selected_option
            },
            reply_topic=reply_topic
        )
