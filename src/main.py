import asyncio
import logging
from src.config import get_settings
from src.brokers.redis_broker import RedisBroker
from src.brokers.sqs_broker import SQSBroker
from src.handlers.router import IntentRouter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def main():
    """Bot startup and async event loop stub."""
    settings = get_settings()
    logger.info("Initializing my-personal-tg-bot Central Gateway...")

    if settings.queue_provider == "redis":
        broker = RedisBroker(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db
        )
    else:
        broker = SQSBroker()

    connected = await broker.connect()
    if connected:
        logger.info(f"Successfully connected to Queue Broker ({settings.queue_provider})")

    router = IntentRouter(broker=broker, settings=settings)
    logger.info("Intent Router initialized. Ready to receive commands.")

    # Main async loop stub
    try:
        logger.info("Gateway service running. Press Ctrl+C to terminate.")
        await asyncio.sleep(1)
    finally:
        await broker.disconnect()
        logger.info("Queue Broker disconnected cleanly.")


if __name__ == "__main__":
    asyncio.run(main())
