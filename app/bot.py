import uuid
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler, Application

from app.config import BOT_TOKEN
from app.weather import get_weather, get_forecast
from app.modes import oracle, scientific, drama


def parse(q):
    parts = q.split()
    city = parts[0]
    mode = parts[1] if len(parts) > 1 else "oracle"
    return city, mode


async def inline(update, context):
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
            title=f"{w['city']} {w['temp']}°C",
            input_message_content=InputTextMessageContent(text)
        )
    ], cache_time=10)


def run():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(InlineQueryHandler(inline))
    app.run_polling()