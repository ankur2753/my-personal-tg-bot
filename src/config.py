import json
import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application Configuration Settings with JSON and Env support."""

    telegram_bot_token: str = Field(default="YOUR_BOTFATHER_TOKEN_HERE")
    allowed_telegram_user_ids: List[int] = Field(default_factory=lambda: [123456789])

    queue_provider: str = Field(default="redis")

    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_password: str = Field(default="secret_redis_pass")
    redis_db: int = Field(default=0)

    aws_region: str = Field(default="us-east-1")
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None

    topic_job_hunt_requests: str = Field(default="agent.job-hunt.requests")
    topic_job_hunt_responses: str = Field(default="agent.job-hunt.responses")
    topic_finance_requests: str = Field(default="agent.finance.requests")
    topic_finance_responses: str = Field(default="agent.finance.responses")
    topic_global_notifications: str = Field(default="notifications.global")

    def is_user_allowed(self, user_id: int) -> bool:
        """Check if a Telegram user ID is whitelisted."""
        return user_id in self.allowed_telegram_user_ids

    @classmethod
    def load_from_json(cls, file_path: str = "appsettings.json") -> "Settings":
        """Load configuration from appsettings.json, with environment variable overrides."""
        data = {}
        path = Path(file_path)
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    raw_json = json.load(f)
                    
                telegram_cfg = raw_json.get("telegram", {})
                queue_cfg = raw_json.get("queue", {})
                redis_cfg = queue_cfg.get("redis", {})
                sqs_cfg = queue_cfg.get("aws_sqs", {})
                topics_cfg = raw_json.get("topics", {})

                if "bot_token" in telegram_cfg:
                    data["telegram_bot_token"] = telegram_cfg["bot_token"]
                if "allowed_user_ids" in telegram_cfg:
                    data["allowed_telegram_user_ids"] = telegram_cfg["allowed_user_ids"]
                if "provider" in queue_cfg:
                    data["queue_provider"] = queue_cfg["provider"]
                
                if "host" in redis_cfg:
                    data["redis_host"] = redis_cfg["host"]
                if "port" in redis_cfg:
                    data["redis_port"] = int(redis_cfg["port"])
                if "password" in redis_cfg:
                    data["redis_password"] = redis_cfg["password"]
                if "db" in redis_cfg:
                    data["redis_db"] = int(redis_cfg["db"])

                if "region" in sqs_cfg:
                    data["aws_region"] = sqs_cfg["region"]
                if "access_key_id" in sqs_cfg:
                    data["aws_access_key_id"] = sqs_cfg["access_key_id"]
                if "secret_access_key" in sqs_cfg:
                    data["aws_secret_access_key"] = sqs_cfg["secret_access_key"]

                if "job_hunt_requests" in topics_cfg:
                    data["topic_job_hunt_requests"] = topics_cfg["job_hunt_requests"]
                if "job_hunt_responses" in topics_cfg:
                    data["topic_job_hunt_responses"] = topics_cfg["job_hunt_responses"]
                if "finance_requests" in topics_cfg:
                    data["topic_finance_requests"] = topics_cfg["finance_requests"]
                if "finance_responses" in topics_cfg:
                    data["topic_finance_responses"] = topics_cfg["finance_responses"]
                if "global_notifications" in topics_cfg:
                    data["topic_global_notifications"] = topics_cfg["global_notifications"]
            except Exception as e:
                pass

        # Environment variable overrides (highest priority)
        if os.getenv("TELEGRAM_BOT_TOKEN"):
            data["telegram_bot_token"] = os.getenv("TELEGRAM_BOT_TOKEN")
        if os.getenv("ALLOWED_TELEGRAM_USER_IDS"):
            data["allowed_telegram_user_ids"] = [
                int(x.strip()) for x in os.getenv("ALLOWED_TELEGRAM_USER_IDS").split(",") if x.strip().isdigit()
            ]
        if os.getenv("QUEUE_PROVIDER"):
            data["queue_provider"] = os.getenv("QUEUE_PROVIDER")
        if os.getenv("REDIS_HOST"):
            data["redis_host"] = os.getenv("REDIS_HOST")
        if os.getenv("REDIS_PORT"):
            data["redis_port"] = int(os.getenv("REDIS_PORT"))
        if os.getenv("REDIS_PASSWORD"):
            data["redis_password"] = os.getenv("REDIS_PASSWORD")

        return cls(**data)


def get_settings(config_path: str = "appsettings.json") -> Settings:
    """Dependency injection helper for loading settings."""
    return Settings.load_from_json(config_path)
