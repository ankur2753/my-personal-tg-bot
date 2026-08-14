import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class MessageEnvelope(BaseModel):
    """Generic Task Payload Schema across all queue topics."""

    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    source_agent: str = Field(default="my-personal-tg-bot")
    target_agent: str
    action: str
    user_id: int
    chat_id: int
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    payload: Dict[str, Any] = Field(default_factory=dict)
    reply_topic: Optional[str] = None

    def to_json_dict(self) -> Dict[str, Any]:
        """Serialize payload to dictionary."""
        return self.model_dump()

    @classmethod
    def from_json_dict(cls, data: Dict[str, Any]) -> "MessageEnvelope":
        """Deserialize payload from dictionary."""
        return cls.model_validate(data)


class JobHuntPayload(BaseModel):
    """Specific payload data for job hunt requests."""

    job_url: Optional[str] = None
    recruiter_profile: Optional[str] = None
    custom_notes: Optional[str] = None
    resume_path: Optional[str] = None
    action_type: str = "TAILOR_RESUME"  # TAILOR_RESUME | COLD_OUTREACH | ATS_CHECK


class JobHuntResponsePayload(BaseModel):
    """Specific payload data for job hunt responses."""

    status: str  # SUCCESS | FAILED | HITL_REQUIRED
    pdf_path: Optional[str] = None
    png_preview_path: Optional[str] = None
    ats_score: Optional[float] = None
    generated_text: Optional[str] = None
    error_message: Optional[str] = None


class FinanceResponsePayload(BaseModel):
    """Specific payload data for finance responses."""

    status: str
    message: Optional[str] = None


class HITLPromptPayload(BaseModel):
    """Payload data for Human-in-the-loop prompts."""

    prompt_id: str = Field(default_factory=lambda: f"hitl_{uuid.uuid4().hex[:8]}")
    question: str
    options: list[str]  # e.g., ["15 Days", "30 Days", "Custom"]
    context_data: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = 300
