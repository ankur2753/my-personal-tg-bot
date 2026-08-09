from abc import ABC, abstractmethod
from typing import Callable, Coroutine, Any, Dict, Optional
from ..models.payload import MessageEnvelope


class BaseQueueBroker(ABC):
    """Abstract interface for pluggable Queue Brokers (Redis Streams, SQS, etc.)."""

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to queue engine."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to queue engine."""
        pass

    @abstractmethod
    async def publish(self, topic: str, envelope: MessageEnvelope) -> str:
        """Publish a message envelope to a specific queue topic. Returns published message ID."""
        pass

    @abstractmethod
    async def subscribe(
        self,
        topic: str,
        handler: Callable[[MessageEnvelope], Coroutine[Any, Any, None]],
        consumer_group: Optional[str] = None
    ) -> None:
        """Subscribe to a topic and dispatch incoming messages to handler coroutine."""
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        """Check connection status."""
        pass
