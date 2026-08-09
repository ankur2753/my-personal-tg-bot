import asyncio
import logging
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from src.config import get_settings
from src.brokers.redis_broker import RedisBroker
from src.brokers.sqs_broker import SQSBroker
from src.handlers.router import IntentRouter
from src.handlers.default_handler import DefaultHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def handle_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command / message handler for welcome menu and listing active functions."""
    user = update.effective_user
    user_id = user.id
    username = user.username
    settings = context.bot_data.get("settings")

    if not settings.is_user_allowed(user_id, username):
        logger.warning(f"Unauthorized access attempt from User ID: {user_id}, Username: @{username}")
        await update.message.reply_text(
            f"⛔ *Unauthorized Access*\n\n"
            f"Your Telegram User ID (`{user_id}`) and Username (`@{username}`) are not listed in `appsettings.json`.",
            parse_mode="Markdown"
        )
        return

    welcome_menu = DefaultHandler.get_welcome_menu()
    await update.message.reply_text(welcome_menu, parse_mode="Markdown")


async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /status command."""
    user = update.effective_user
    user_id = user.id
    username = user.username
    settings = context.bot_data.get("settings")
    broker = context.bot_data.get("broker")

    if not settings.is_user_allowed(user_id, username):
        await update.message.reply_text("⛔ Unauthorized access.")
        return

    is_connected = await broker.is_connected()
    status_msg = (
        "🟢 *my-personal-tg-bot Central Gateway Status*\n\n"
        f"• *User:* `@{username}` (`{user_id}`)\n"
        f"• *Queue Provider:* `{settings.queue_provider}`\n"
        f"• *Broker Connected:* `{is_connected}`\n"
        f"• *Allowed Whitelist:* `{settings.allowed_telegram_user_ids}`\n"
        f"• *Target Job Queue:* `{settings.topic_job_hunt_requests}`"
    )
    await update.message.reply_text(status_msg, parse_mode="Markdown")


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main message handler for text updates."""
    user = update.effective_user
    user_id = user.id
    username = user.username
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    settings = context.bot_data.get("settings")
    router: IntentRouter = context.bot_data.get("router")

    if not settings.is_user_allowed(user_id, username):
        logger.warning(f"Unauthorized message from User ID: {user_id}, Username: @{username}")
        await update.message.reply_text(
            f"⛔ Unauthorized user (ID: `{user_id}`, Username: `@{username}`).",
            parse_mode="Markdown"
        )
        return

    intent = router.detect_intent(text)
    logger.info(f"Received message from @{username} (ID: {user_id}): '{text}' -> Intent: {intent}")

    if intent in ["welcome", "default"]:
        await handle_welcome(update, context)
        return

    if intent == "job-hunt":
        try:
            envelope = await router.route_message(text=text, user_id=user_id, chat_id=chat_id)
            if envelope:
                reply_text = (
                    "🚀 *Job Hunt Request Queued!*\n\n"
                    f"• *Action:* `{envelope.action}`\n"
                    f"• *Message ID:* `{envelope.message_id}`\n"
                    f"• *Queue Topic:* `{settings.topic_job_hunt_requests}`\n\n"
                    "Processing resume tailoring with `jobHunt` agent..."
                )
                await update.message.reply_text(reply_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error routing message: {e}")
            await update.message.reply_text(f"❌ Error queueing request: {e}")
        return

    await handle_welcome(update, context)


async def async_main():
    """Bot application async entrypoint."""
    settings = get_settings()
    logger.info("Initializing my-personal-tg-bot Central Gateway...")

    if settings.telegram_bot_token == "YOUR_BOTFATHER_TOKEN_HERE":
        logger.warning(
            "----------------------------------------------------------------------\n"
            "⚠️ TELEGRAM_BOT_TOKEN is set to default placeholder in appsettings.json!\n"
            "Please update `telegram.bot_token` in `appsettings.json` with your real\n"
            "bot token from @BotFather to receive updates from Telegram.\n"
            "----------------------------------------------------------------------"
        )

    if settings.queue_provider == "redis":
        broker = RedisBroker(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db
        )
    else:
        broker = SQSBroker()

    await broker.connect()

    router = IntentRouter(broker=broker, settings=settings)

    app = ApplicationBuilder().token(settings.telegram_bot_token).build()

    app.bot_data["settings"] = settings
    app.bot_data["broker"] = broker
    app.bot_data["router"] = router

    app.add_handler(CommandHandler("start", handle_welcome))
    app.add_handler(CommandHandler("help", handle_welcome))
    app.add_handler(CommandHandler("status", handle_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    logger.info("Telegram Gateway Polling started. Press Ctrl+C to stop.")
    
    async with app:
        await app.start()
        await app.updater.start_polling()
        # Keep polling running asynchronously
        while True:
            await asyncio.sleep(3600)


def main():
    try:
        asyncio.run(async_main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Gateway service stopped cleanly.")


if __name__ == "__main__":
    main()
