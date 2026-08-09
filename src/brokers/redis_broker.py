import json
import logging
from typing import Callable, Coroutine, Any, Optional, Dict
import redis.asyncio as aioredis
from .base_broker import BaseQueueBroker
from ..models.payload import MessageEnvelope

logger = logging.getLogger(__name__)


class RedisBroker(BaseQueueBroker):
    """Redis Streams Queue Broker implementation using redis.asyncio."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: str = "secret_redis_pass",
        db: int = 0,
        mock_mode: bool = False
    ):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.mock_mode = mock_mode
        self._client: Optional[aioredis.Redis] = None
        self._connected = False
        self._published_messages: Dict[str, list[MessageEnvelope]] = {}

    async def connect(self) -> bool:
        """Establish connection to Redis Streams engine."""
        if self.mock_mode:
            self._connected = True
            return True

        try:
            self._client = aioredis.Redis(
                host=self.host,
                port=self.port,
                password=self.password if self.password else None,
                db=self.db,
                decode_responses=True
            )
            await self._client.ping()
            self._connected = True
            logger.info(f"Connected to live Redis Streams at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.info(f"Redis host {self.host}:{self.port} unreachable ({e}). Operating in fallback/in-memory queue mode.")
            self.mock_mode = True
            self._connected = True
            return True

    async def disconnect(self) -> None:
        """Close Redis connection cleanly."""
        if self._client and not self.mock_mode:
            try:
                await self._client.aclose()
            except Exception:
                pass
        self._connected = False
        self._client = None

    async def is_connected(self) -> bool:
        return self._connected

    async def publish(self, topic: str, envelope: MessageEnvelope) -> str:
        """Publish message envelope to Redis Stream (XADD)."""
        if not self._connected:
            raise ConnectionError("RedisBroker is not connected.")

        json_data = json.dumps(envelope.to_json_dict())

        if self.mock_mode or not self._client:
            if topic not in self._published_messages:
                self._published_messages[topic] = []
            self._published_messages[topic].append(envelope)
            return envelope.message_id

        # Publish to real Redis Stream via XADD
        msg_id = await self._client.xadd(topic, {"envelope": json_data})
        return str(msg_id)

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[MessageEnvelope], Coroutine[Any, Any, None]],
        consumer_group: Optional[str] = "tg_bot_group"
    ) -> None:
        """Subscribe to Redis Stream topic using Consumer Groups (XREADGROUP)."""
        if not self._connected:
            raise ConnectionError("RedisBroker is not connected.")

        if self.mock_mode or not self._client:
            if topic in self._published_messages:
                for envelope in self._published_messages[topic]:
                    await handler(envelope)
            return

        group_name = consumer_group or "tg_bot_group"
        consumer_name = "consumer_1"

        try:
            await self._client.xgroup_create(topic, group_name, id="0", mkstream=True)
        except Exception as e:
            if "BUSYGROUP" not in str(e):
                logger.debug(f"Consumer group note: {e}")

        response = await self._client.xreadgroup(group_name, consumer_name, {topic: ">"}, count=10, block=1000)
        if response:
            for stream_name, messages in response:
                for msg_id, msg_data in messages:
                    if "envelope" in msg_data:
                        envelope_dict = json.loads(msg_data["envelope"])
                        envelope = MessageEnvelope.from_json_dict(envelope_dict)
                        await handler(envelope)
                        await self._client.xack(topic, group_name, msg_id)
