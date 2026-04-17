from telegram.ext import Application, CommandHandler, MessageHandler, filters

from app.config import TELEGRAM_BOT_TOKEN
from app.handlers import (
    start_command,
    help_command,
    text_handler,
    voice_handler,
)


def create_app() -> Application:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.VOICE, voice_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    return application