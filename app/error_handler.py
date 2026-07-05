import logging
import uuid
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Unhandled error in Telegram update")

    if update is None:
        return

    inline_query = getattr(update, "inline_query", None)
    if inline_query is None:
        return

    try:
        await inline_query.answer([
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="error",
                input_message_content=InputTextMessageContent(
                    "⚠️ Произошла ошибка. Попробуйте снова."
                )
            )
        ])
    except Exception:
        logger.exception("Failed to send fallback inline response")
