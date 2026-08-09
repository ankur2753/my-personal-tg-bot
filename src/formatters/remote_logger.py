import json
import logging
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def send_http_post(url: str, payload: Dict[str, Any], timeout: float = 10.0) -> bool:
    """Send HTTP POST request with JSON payload to Google Sheets Webhook URL."""
    try:
        import urllib.request
        json_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=json_bytes,
            headers={"Content-Type": "application/json", "User-Agent": "my-personal-tg-bot/2.0"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.getcode() in (200, 201, 302)
    except Exception as e:
        logger.warning(f"Fail-safe logger: Failed to post to Google Sheets Webhook ({url}): {e}")
        return False


def log_resume_creation_to_sheets(
    webhook_url: Optional[str],
    company: str,
    status: str,
    local_filepath: str,
    timestamp: Optional[str] = None,
    async_exec: bool = True
) -> bool:
    """Logs resume creation results directly to Google Sheets 'Resume Logs' sheet.

    Args:
        webhook_url: Google Apps Script Web App URL.
        company: Name of hiring company for which resume was created.
        status: Result status ("PASS" | "FAILED").
        local_filepath: Local file path of generated resume PDF.
        timestamp: Result ISO/UTC timestamp.
        async_exec: If True, dispatches request in background thread.
    """
    if not webhook_url or not webhook_url.strip():
        logger.debug("No google_sheets_webhook_url configured. Skipping remote log.")
        return False

    if not timestamp:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    payload = {
        "log_type": "resume_tailoring",
        "result_time": timestamp,
        "status": str(status).upper(),
        "company": str(company or "Unknown Company"),
        "local_filepath": str(local_filepath or "N/A")
    }

    if async_exec:
        thread = threading.Thread(
            target=send_http_post,
            args=(webhook_url.strip(), payload),
            daemon=True,
            name="ResumeSheetsLoggerThread"
        )
        thread.start()
        return True
    else:
        return send_http_post(webhook_url.strip(), payload)
