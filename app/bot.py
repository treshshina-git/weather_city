import uuid
import logging
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import InlineQueryHandler, Application, ContextTypes

from app.config import BOT_TOKEN
from app.weather import get_weather, get_forecast
from app.modes import oracle, scientific, drama

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def parse(q):
    parts = q.split()
    city = parts[0]
    mode = parts[1] if len(parts) > 1 else "scientific"
    return city, mode


async def inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.inline_query.query.strip()
    if not q:
        return

    try:
        city, mode = parse(q)

        w = get_weather(city)
        f = get_forecast(city)

        if not w or not f:
            await update.inline_query.answer([
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="not found",
                    input_message_content=InputTextMessageContent("🌪 no data")
                )
            ])
            return

        if mode == "oracle":
            text = oracle(w["temp"])
        elif mode == "drama":
            text = drama(w)
        else:
            text = scientific(w)

        await update.inline_query.answer([
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"{w['city']} {round(w['temp'])}°C",
                input_message_content=InputTextMessageContent(text, parse_mode="HTML")
            )
        ], cache_time=10)
    except Exception as exc:
        logger.exception("Inline query handling failed")
        await update.inline_query.answer([
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="error",
                input_message_content=InputTextMessageContent("⚠️ Произошла ошибка. Попробуйте снова.")
            )
        ])


def run():
    app = Application.builder().token(BOT_TOKEN).build()
    #app.bot.delete_webhook(drop_pending_updates=True)
    app.add_handler(InlineQueryHandler(inline))
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )