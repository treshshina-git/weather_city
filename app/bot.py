import uuid
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import InlineQueryHandler, Application, ContextTypes

from app.config import BOT_TOKEN
from app.error_handler import error_handler
from app.weather import get_weather, get_forecast
from app.modes import oracle, scientific, drama


def parse(q):
    parts = q.split()
    city = parts[0]
    mode = parts[1] if len(parts) > 1 else "scientific"
    return city, mode


async def inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.inline_query.query.strip()
    if not q:
        return

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


def run():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_error_handler(error_handler)
    #app.bot.delete_webhook(drop_pending_updates=True)
    app.add_handler(InlineQueryHandler(inline))
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )