import re


class TelegramFormatter:
    """Formatter helper for escaping Telegram MarkdownV2 reserved characters."""

    RESERVED_CHARS = r"\_*[]()~`>#+-=|{}.!"

    @classmethod
    def escape_markdown_v2(cls, text: str) -> str:
        """Escape reserved characters for MarkdownV2."""
        return re.sub(f"([{re.escape(cls.RESERVED_CHARS)}])", r"\\\1", text)

    @classmethod
    def format_job_response(cls, status: str, ats_score: float = None, pdf_path: str = None) -> str:
        """Format response message for candidate."""
        lines = [f"💼 *Job Agent Status:* `{status}`"]
        if ats_score is not None:
            lines.append(f"📊 *ATS Match Score:* `{ats_score:.1f}%`")
        if pdf_path:
            lines.append(f"📄 *Tailored Resume:* Attached below")
        return "\n".join(lines)
