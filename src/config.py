import os
from typing import List
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application Configuration Settings."""

    telegram_bot_token: str = Field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", "dummy_token"))
    allowed_telegram_user_ids: List[int] = Field(
        default_factory=lambda: [
            int(x.strip()) for x in os.getenv("ALLOWED_TELEGRAM_USER_IDS", "123456789").split(",") if x.strip().isdigit()
        ]
    )

    queue_provider: str = Field(default_factory=lambda: os.getenv("QUEUE_PROVIDER", "redis"))

    redis_host: str = Field(default_factory=lambda: os.getenv("REDIS_HOST", "localhost"))
    redis_port: int = Field(default_factory=lambda: int(os.getenv("REDIS_PORT", "6379")))
    redis_password: str = Field(default_factory=lambda: os.getenv("REDIS_PASSWORD", "secret_redis_pass"))
    redis_db: int = Field(default_factory=lambda: int(os.getenv("REDIS_DB", "0")))

    topic_job_hunt_requests: str = Field(default_factory=lambda: os.getenv("TOPIC_JOB_HUNT_REQUESTS", "agent.job-hunt.requests"))
    topic_job_hunt_responses: str = Field(default_factory=lambda: os.getenv("TOPIC_JOB_HUNT_RESPONSES", "agent.job-hunt.responses"))
    topic_finance_requests: str = Field(default_factory=lambda: os.getenv("TOPIC_FINANCE_REQUESTS", "agent.finance.requests"))
    topic_finance_responses: str = Field(default_factory=lambda: os.getenv("TOPIC_FINANCE_RESPONSES", "agent.finance.responses"))
    topic_global_notifications: str = Field(default_factory=lambda: os.getenv("TOPIC_GLOBAL_NOTIFICATIONS", "notifications.global"))

    def is_user_allowed(self, user_id: int) -> bool:
        """Check if a Telegram user ID is whitelisted."""
        return user_id in self.allowed_telegram_user_ids


def get_settings() -> Settings:
    """Dependency injection helper for loading settings."""
    return Settings()
