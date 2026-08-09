class DefaultHandler:
    """Fallback handler for help, status, and unknown commands."""

    @staticmethod
    def get_help_text() -> str:
        return (
            "🤖 *my-personal-tg-bot Central Control Center*\n\n"
            "Supported Agents & Commands:\n"
            "• *Job Search Agent*: Send job posting URL (LinkedIn/Naukri) or `/job` command.\n"
            "• *Finance Agent*: Send `/expense 500 groceries` or receipt photos.\n"
            "• *Status*: `/status` to inspect queue health and connected agents."
        )
