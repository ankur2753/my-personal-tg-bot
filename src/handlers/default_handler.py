class DefaultHandler:
    """Handler for welcome messages, help menu, and listing active agent features."""

    @staticmethod
    def get_welcome_menu() -> str:
        """Return formatted welcome menu listing active functions."""
        return (
            "👋 *Welcome to your Personal AI Command Center!*\n\n"
            "Here are your currently available agent functions:\n\n"
            "💼 *1. Tailored Resume & Auto-Apply*\n"
            "• Send any job posting link (LinkedIn, Naukri, Company Careers page) or use `/job <url>`.\n"
            "• The Job Search Agent will automatically tailor your resume, calculate ATS match scores, and instantly apply on Naukri.\n\n"
            "🤝 *2. Automated Referral Finder*\n"
            "• Use `/referral <Company> | <Role>` or `/referral <url> | <Company>`.\n"
            "• The agent will navigate LinkedIn, score top peers, and generate personalized cold outreach DMs.\n\n"
            "🤖 *3. Human-In-The-Loop (Visual Fallback)*\n"
            "• If the bot gets stuck on a complex form or 2FA, it will pause and message you here!\n"
            "• Use `/answer <your response>` to guide the AI and resume the automation.\n\n"
            "ℹ️ *System Commands:*\n"
            "• `/status` — Inspect Queue Broker and Agent ecosystem health.\n"
            "• `/help` — Display this capabilities menu anytime."
        )

    @staticmethod
    def get_help_text() -> str:
        """Alias for help menu."""
        return DefaultHandler.get_welcome_menu()
