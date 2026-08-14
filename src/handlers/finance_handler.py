from ..brokers.base_broker import BaseQueueBroker
from ..models.payload import MessageEnvelope, FinanceResponsePayload


class FinanceHandler:
    """Handler stub for future finance agent integration."""

    def __init__(self, broker: BaseQueueBroker):
        self.broker = broker

    def create_request_envelope(self, user_id: int, chat_id: int, text: str) -> MessageEnvelope:
        return MessageEnvelope(
            target_agent="finance-agent",
            action="LOG_EXPENSE",
            user_id=user_id,
            chat_id=chat_id,
            payload={"raw_text": text},
            reply_topic="agent.finance.responses"
        )

    def parse_response_envelope(self, envelope: MessageEnvelope) -> FinanceResponsePayload:
        """Parse incoming MessageEnvelope from finance response queue."""
        return FinanceResponsePayload.model_validate(envelope.payload)
