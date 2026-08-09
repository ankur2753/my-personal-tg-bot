from typing import Callable, Coroutine, Any, Optional
from .base_broker import BaseQueueBroker
from ..models.payload import MessageEnvelope


class SQSBroker(BaseQueueBroker):
    """AWS SQS Queue Broker implementation.
    
    Phase 1 (M1) Deliverable: SQS boto3 client wrapper.
    """

    def __init__(self, region: str = "us-east-1", access_key_id: Optional[str] = None, secret_access_key: Optional[str] = None):
        self.region = region
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self._connected = False

    async def connect(self) -> bool:
        raise NotImplementedError("Phase 1 (M1) Pending: SQS client initialization is not implemented yet.")

    async def disconnect(self) -> None:
        self._connected = False

    async def is_connected(self) -> bool:
        return self._connected

    async def publish(self, topic: str, envelope: MessageEnvelope) -> str:
        raise NotImplementedError("Phase 1 (M1) Pending: SQS SendMessage is not implemented yet.")

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[MessageEnvelope], Coroutine[Any, Any, None]],
        consumer_group: Optional[str] = None
    ) -> None:
        raise NotImplementedError("Phase 1 (M1) Pending: SQS ReceiveMessage long-polling loop is not implemented yet.")
