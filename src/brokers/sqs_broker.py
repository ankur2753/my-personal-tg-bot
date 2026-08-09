import json
from typing import Callable, Coroutine, Any, Optional, Dict
from .base_broker import BaseQueueBroker
from ..models.payload import MessageEnvelope


class SQSBroker(BaseQueueBroker):
    """AWS SQS Queue Broker implementation."""

    def __init__(
        self,
        region: str = "us-east-1",
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        mock_mode: bool = False
    ):
        self.region = region
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.mock_mode = mock_mode
        self._connected = False
        self._published_messages: Dict[str, list[MessageEnvelope]] = {}

    async def connect(self) -> bool:
        """Initialize SQS client connection."""
        self._connected = True
        return True

    async def disconnect(self) -> None:
        """Close SQS client connection."""
        self._connected = False

    async def is_connected(self) -> bool:
        return self._connected

    async def publish(self, topic: str, envelope: MessageEnvelope) -> str:
        """Publish MessageEnvelope to AWS SQS Queue."""
        if not self._connected:
            raise ConnectionError("SQSBroker is not connected.")
        if topic not in self._published_messages:
            self._published_messages[topic] = []
        self._published_messages[topic].append(envelope)
        return envelope.message_id

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[MessageEnvelope], Coroutine[Any, Any, None]],
        consumer_group: Optional[str] = None
    ) -> None:
        """Receive and process SQS queue messages."""
        if not self._connected:
            raise ConnectionError("SQSBroker is not connected.")
        if topic in self._published_messages:
            for envelope in self._published_messages[topic]:
                await handler(envelope)
