from typing import Dict, Any, Optional
from ..brokers.base_broker import BaseQueueBroker
from ..models.payload import MessageEnvelope, JobHuntPayload, JobHuntResponsePayload


class JobAgentHandler:
    """Handler for job search related request/response transformations."""

    def __init__(self, broker: BaseQueueBroker):
        self.broker = broker

    def create_request_envelope(self, user_id: int, chat_id: int, job_payload: JobHuntPayload) -> MessageEnvelope:
        """Construct a standardized MessageEnvelope for job hunt request."""
        return MessageEnvelope(
            target_agent="job-hunt-agent",
            action=job_payload.action_type,
            user_id=user_id,
            chat_id=chat_id,
            payload=job_payload.model_dump(),
            reply_topic="agent.job-hunt.responses"
        )

    def parse_response_envelope(self, envelope: MessageEnvelope) -> JobHuntResponsePayload:
        """Parse incoming MessageEnvelope from job hunt response queue."""
        return JobHuntResponsePayload.model_validate(envelope.payload)
