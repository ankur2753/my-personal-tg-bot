import re
from typing import Dict, Any, Optional
from ..brokers.base_broker import BaseQueueBroker
from ..models.payload import MessageEnvelope
from ..config import Settings


class IntentRouter:
    """Master Intent Router for classifying Telegram messages and routing to specific Queue topics."""

    def __init__(self, broker: BaseQueueBroker, settings: Settings):
        self.broker = broker
        self.settings = settings

    def detect_intent(self, text: str) -> str:
        """Classify message intent based on pattern matching or slash commands.
        
        Returns:
            "welcome" | "job-hunt" | "finance" | "hitl" | "default"
        """
        text_lower = text.strip().lower()
        if text_lower in ["hi", "hello", "hey", "start", "/start", "/help", "help"]:
            return "welcome"
        elif text_lower.startswith("/referal") or text_lower.startswith("/referral"):
            return "referral"
        elif text_lower.startswith("/job") or "linkedin.com/jobs" in text_lower or "naukri.com" in text_lower or "careers" in text_lower or text_lower.startswith("http"):
            return "job-hunt"
        elif text_lower.startswith("/expense") or text_lower.startswith("/finance") or "budget" in text_lower:
            return "finance"
        elif text_lower.startswith("/hitl") or text_lower.startswith("/answer"):
            return "hitl"
        elif text_lower.startswith("/process_referrals") or text_lower.startswith("/process_pending"):
            return "process-referrals"
        elif text_lower.startswith("/scrape_jobs") or text_lower.startswith("/scrape"):
            return "scrape-jobs"
        elif text_lower.startswith("/hunt"):
            return "scrape-and-draft"
        return "default"

    async def route_message(self, text: str, user_id: int, chat_id: int, extra_payload: Optional[Dict[str, Any]] = None) -> Optional[MessageEnvelope]:
        """Process incoming message, build envelope, publish to corresponding topic."""
        if not self.settings.is_user_allowed(user_id, ""):
            raise PermissionError(f"User {user_id} is not authorized.")

        intent = self.detect_intent(text)
        payload = extra_payload or {}

        if intent == "job-hunt":
            from .job_agent_handler import JobAgentHandler
            from ..models.payload import JobHuntPayload
            
            job_handler = JobAgentHandler(self.broker)
            
            url = None
            jd_text = text
            company = None
            role = None
            
            import re
            if "|" in text:
                parts = [p.strip() for p in text.split("|")]
                for p in parts:
                    if p.startswith("http"):
                        url = p
                    elif not company:
                        company = p
                    elif not role:
                        role = p
                jd_text = ""
            else:
                url_match = re.search(r'(https?://[^\s]+)', text)
                if url_match:
                    url = url_match.group(1)
                    jd_text = text.replace(url, '').strip()

            job_payload = JobHuntPayload(
                job_url=url,
                custom_notes=jd_text,
                company=company,
                role=role,
                action_type="TAILOR_RESUME" if url else "GENERAL_JOB_QUERY"
            )
            
            envelope = job_handler.create_request_envelope(
                user_id=user_id,
                chat_id=chat_id,
                job_payload=job_payload
            )
            topic = self.settings.topic_job_hunt_requests
            
        elif intent == "referral":
            from .job_agent_handler import JobAgentHandler
            from ..models.payload import JobHuntPayload
            
            job_handler = JobAgentHandler(self.broker)
            
            url = None
            jd_text = text.replace("/referal", "").replace("/referral", "").strip()
            company = None
            role = None
            
            import re
            if "|" in jd_text:
                parts = [p.strip() for p in jd_text.split("|")]
                for p in parts:
                    if p.startswith("http"):
                        url = p
                    elif not company:
                        company = p
                    elif not role:
                        role = p
                jd_text = ""
            else:
                url_match = re.search(r'(https?://[^\s]+)', jd_text)
                if url_match:
                    url = url_match.group(1)
                
            job_payload = JobHuntPayload(
                job_url=url,
                custom_notes=jd_text,
                company=company,
                role=role,
                action_type="SEEK_REFERRAL"
            )
            
            envelope = job_handler.create_request_envelope(
                user_id=user_id,
                chat_id=chat_id,
                job_payload=job_payload
            )
            topic = self.settings.topic_job_hunt_requests
            
        elif intent == "finance":
            topic = self.settings.topic_finance_requests
            envelope = MessageEnvelope(
                target_agent="finance-agent",
                action="LOG_EXPENSE",
                user_id=user_id,
                chat_id=chat_id,
                payload=payload,
                reply_topic=self.settings.topic_finance_responses
            )
        elif intent == "process-referrals":
            from .job_agent_handler import JobAgentHandler
            from ..models.payload import JobHuntPayload
            
            job_handler = JobAgentHandler(self.broker)
            job_payload = JobHuntPayload(
                action_type="PROCESS_PENDING_REFERRALS"
            )
            envelope = job_handler.create_request_envelope(user_id, chat_id, job_payload)
            topic = self.settings.topic_job_hunt_requests
            
        elif intent == "scrape-jobs":
            from .job_agent_handler import JobAgentHandler
            from ..models.payload import JobHuntPayload
            
            job_handler = JobAgentHandler(self.broker)
            # You can parse keywords/location from the text later, for now we will send the text
            job_payload = JobHuntPayload(
                custom_notes=text.replace("/scrape_jobs", "").replace("/scrape", "").strip(),
                action_type="SCRAPE_JOBS"
            )
            envelope = job_handler.create_request_envelope(user_id, chat_id, job_payload)
            topic = self.settings.topic_job_hunt_requests

        elif intent == "scrape-and-draft":
            from .job_agent_handler import JobAgentHandler
            from ..models.payload import JobHuntPayload
            
            job_handler = JobAgentHandler(self.broker)
            job_payload = JobHuntPayload(
                custom_notes=text.replace("/hunt", "").strip(),
                action_type="SCRAPE_AND_DRAFT"
            )
            envelope = job_handler.create_request_envelope(user_id, chat_id, job_payload)
            topic = self.settings.topic_job_hunt_requests

        else:
            return None

        await self.broker.publish(topic, envelope)
        return envelope
