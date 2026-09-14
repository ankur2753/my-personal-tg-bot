import asyncio
import logging
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from src.config import get_settings
from src.brokers.redis_broker import RedisBroker
from src.brokers.sqs_broker import SQSBroker
from src.handlers.router import IntentRouter
from src.handlers.default_handler import DefaultHandler
from src.handlers.job_agent_handler import JobAgentHandler
from src.handlers.hitl_handler import HITLHandler
from src.formatters.telegram_formatter import TelegramFormatter
from src.models.payload import MessageEnvelope, HITLPromptPayload

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
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

    if intent == "referral":
        try:
            envelope = await router.route_message(text=text, user_id=user_id, chat_id=chat_id)
            if envelope:
                reply_text = (
                    "🎯 *Referral Request Queued!*\n\n"
                    f"• *Queue Topic:* `{settings.topic_job_hunt_requests}`\n\n"
                    "Extracting job details and searching for referral candidates..."
                )
                await update.message.reply_text(reply_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error routing message: {e}")
            await update.message.reply_text(f"❌ Error queueing request: {e}")
        return

    if intent == "finance":
        try:
            envelope = await router.route_message(text=text, user_id=user_id, chat_id=chat_id)
            if envelope:
                reply_text = (
                    "💸 *Finance Request Queued!*\n\n"
                    f"Message ID: `{envelope.message_id}`\n"
                    f"Agent: `{envelope.target_agent}`\n\n"
                    "_I'll ping you once the transaction is processed!_"
                )
                await update.message.reply_text(reply_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error routing message: {e}")
            await update.message.reply_text(f"❌ Error queueing request: {e}")
        return

    if intent in ["process-referrals", "scrape-jobs", "scrape-and-draft"]:
        try:
            envelope = await router.route_message(text=text, user_id=user_id, chat_id=chat_id)
            if envelope:
                reply_text = (
                    "🚀 *Job Scraper/Referral Request Queued!*\n\n"
                    f"Message ID: `{envelope.message_id}`\n"
                    f"Action: `{envelope.action}`\n\n"
                    "_I'll ping you once the task is finished!_"
                )
                await update.message.reply_text(reply_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error routing message: {e}")
            await update.message.reply_text(f"❌ Error queueing request: {e}")
        return

    await update.message.reply_text("🤷 *Unknown Intent*\nI'm not sure how to handle this request. Please use /help.", parse_mode="Markdown")


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for inline keyboard callbacks."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    username = user.username
    chat_id = update.effective_chat.id
    settings = context.bot_data.get("settings")
    broker = context.bot_data.get("broker")

    if not settings.is_user_allowed(user_id, username):
        logger.warning(f"Unauthorized callback from User ID: {user_id}")
        await query.edit_message_text(text="⛔ Unauthorized user.")
        return

    data = query.data
    logger.info(f"Received callback: {data}")
    
    if data.startswith("hitl:"):
        parts = data.split(":")
        if len(parts) == 3:
            prompt_id = parts[1]
            option_idx = int(parts[2])
            
            selected_option = "Unknown"
            if query.message and query.message.reply_markup:
                for row in query.message.reply_markup.inline_keyboard:
                    for button in row:
                        if button.callback_data == data:
                            selected_option = button.text
                            break

            envelope = HITLHandler.create_answer_envelope(
                user_id=user_id,
                chat_id=chat_id,
                prompt_id=prompt_id,
                selected_option=selected_option,
                target_agent="job-hunt-agent",
                reply_topic=settings.topic_job_hunt_requests
            )
            
            await broker.publish(
                topic=settings.topic_job_hunt_requests,
                message=envelope.to_json_dict()
            )
            
            await query.edit_message_text(
                text=f"✅ *You selected:* `{selected_option}`\n_Response sent to agent._",
                parse_mode="Markdown"
            )


async def consume_job_responses(app, broker, settings):
    logger.info(f"Starting consumer loop for topic: {settings.topic_job_hunt_responses}")
    job_handler = JobAgentHandler(broker)

    async def handle_response(envelope: MessageEnvelope):
        try:
            if envelope.action == "HITL_PROMPT":
                hitl_payload = HITLPromptPayload.model_validate(envelope.payload)
                keyboard_dicts = HITLHandler.format_hitl_inline_keyboard(hitl_payload)
                keyboard = [[InlineKeyboardButton(**btn) for btn in row] for row in keyboard_dicts]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                text = f"❓ *Question from Agent:*\n\n{hitl_payload.question}"
                await app.bot.send_message(
                    chat_id=envelope.chat_id, 
                    text=text, 
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
                return

            response = job_handler.parse_response_envelope(envelope)
            chat_id = envelope.chat_id

            text = TelegramFormatter.format_job_response(
                status=response.status,
                ats_score=response.ats_score,
                pdf_path=response.pdf_path
            )

            if response.md_path:
                try:
                    with open(response.md_path, 'r', encoding='utf-8') as md_file:
                        md_content = md_file.read()
                        text += f"\n\n{md_content}"
                except Exception as file_e:
                    logger.error(f"Error reading md file: {file_e}")
                    text += f"\n\n⚠️ Could not load drafted text from file. Error: `{file_e}`"
            elif response.generated_text:
                text += f"\n\n📝 *DM/Email Draft:*\n```text\n{response.generated_text}\n```"

            if response.error_message:
                text += f"\n\n❌ *Error:* `{response.error_message}`"

            await app.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")

            if response.pdf_path:
                try:
                    with open(response.pdf_path, 'rb') as pdf_file:
                        await app.bot.send_document(
                            chat_id=chat_id,
                            document=pdf_file,
                            filename="tailored_resume.pdf"
                        )
                except Exception as file_e:
                    logger.error(f"Error opening PDF file: {file_e}")
                    await app.bot.send_message(
                        chat_id=chat_id,
                        text=f"⚠️ Could not load the tailored resume PDF. Error: `{file_e}`",
                        parse_mode="Markdown"
                    )
        except Exception as e:
            logger.error(f"Error handling job response: {e}")

    while True:
        try:
            await broker.subscribe(
                topic=settings.topic_job_hunt_responses,
                handler=handle_response,
                consumer_group="tg_bot_group"
            )
        except Exception as e:
            logger.error(f"Consumer loop error: {e}")
        await asyncio.sleep(1)


async def consume_finance_responses(app, broker, settings):
    logger.info(f"Starting consumer loop for topic: {settings.topic_finance_responses}")
    from src.handlers.finance_handler import FinanceHandler
    finance_handler = FinanceHandler(broker)

    async def handle_response(envelope: MessageEnvelope):
        try:
            response = finance_handler.parse_response_envelope(envelope)
            chat_id = envelope.chat_id

            text = f"💸 *Finance Update:* `{response.status}`"
            if response.message:
                text += f"\n\n{response.message}"

            await app.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error handling finance response: {e}")

    while True:
        try:
            await broker.subscribe(
                topic=settings.topic_finance_responses,
                handler=handle_response,
                consumer_group="tg_bot_finance_group"
            )
        except Exception as e:
            logger.error(f"Consumer loop error: {e}")
        await asyncio.sleep(1)


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

    app = ApplicationBuilder().token(settings.telegram_bot_token).connect_timeout(60.0).read_timeout(60.0).build()

    app.bot_data["settings"] = settings
    app.bot_data["broker"] = broker
    app.bot_data["router"] = router

    app.add_handler(CommandHandler("start", handle_welcome))
    app.add_handler(CommandHandler("help", handle_welcome))
    app.add_handler(CommandHandler("status", handle_status))
    app.add_handler(MessageHandler(filters.TEXT, handle_text_message))
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    logger.info("Telegram Gateway Polling started. Press Ctrl+C to stop.")
    
    async with app:
        await app.start()
        await app.updater.start_polling()
        
        # Start background consumer tasks
        job_agent_task = asyncio.create_task(
            consume_job_responses(app, broker, settings)
        )
        
        finance_agent_task = asyncio.create_task(
            consume_finance_responses(app, broker, settings)
        )
        
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
