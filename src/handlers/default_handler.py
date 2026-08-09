class DefaultHandler:
    """Handler for welcome messages, help menu, and listing active agent features."""

    @staticmethod
    def get_welcome_menu() -> str:
        """Return formatted welcome menu listing active functions."""
        return (
            "👋 *Welcome to your Personal AI Command Center!*\n\n"
            "Here are your currently available agent functions:\n\n"
            "💼 *1. Tailored Resume Generator*\n"
            "• Send any job posting link (LinkedIn, Naukri, Company Careers page) or use `/job <url>`.\n"
            "• The Job Search Agent will automatically tailor your resume, calculate ATS match scores, and generate cold outreach DMs!\n\n"
            "ℹ️ *System Commands:*\n"
            "• `/status` — Inspect Queue Broker and Agent ecosystem health.\n"
            "• `/help` — Display this capabilities menu anytime."
        )

    @staticmethod
    def get_help_text() -> str:
        """Alias for help menu."""
        return DefaultHandler.get_welcome_menu()
