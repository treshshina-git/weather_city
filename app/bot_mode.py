import requests, os
import uuid
from cachetools import TTLCache

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import Application, InlineQueryHandler, ContextTypes

from app.error_handler import error_handler

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

cache = TTLCache(maxsize=300, ttl=300)

# =========================
# 🌍 API
# =========================
def get_weather(city):
    key = f"w:{city}"
    if key in cache:
        return cache[key]

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    r = requests.get(url, params=params)
    if r.status_code != 200:
        return None

    d = r.json()

    data = {
        "city": d["name"],
        "temp": d["main"]["temp"],
        "feels": d["main"]["feels_like"],
        "pressure": d["main"]["pressure"],
        "humidity": d["main"]["humidity"],
        "wind": d["wind"]["speed"],
        "code": d["weather"][0]["id"]
    }

    cache[key] = data
    return data


def get_forecast(city):
    key = f"f:{city}"
    if key in cache:
        return cache[key]

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    r = requests.get(url, params=params)
    if r.status_code != 200:
        return None

    d = r.json()

    days = {}

    for i in d["list"]:
        day = i["dt_txt"].split(" ")[0]
        days.setdefault(day, []).append(i["main"]["temp"])

    result = [
        {"day": k, "temp": round(sum(v)/len(v), 1)}
        for k, v in list(days.items())[:5]
    ]

    cache[key] = result
    return result


# =========================
# 🎭 MODES
# =========================

def mode_parse(q):
    parts = q.split()
    city = parts[0]
    mode = parts[1].lower() if len(parts) > 1 else "science"
    return city, mode


# =========================
# 🎓 SCIENCE MODE
# =========================
def render_science(w, f):
    text = f"""
🌍 {w['city']}

🌡 Температура: {w['temp']}°C
🫧 Ощущается: {w['feels']}°C
💨 Ветер: {w['wind']} м/с
🧭 Давление: {w['pressure']} hPa
💧 Влажность: {w['humidity']}%

📊 5-day forecast:
"""

    for d in f:
        text += f"{d['day']}: {d['temp']}°C\n"

    return text


# =========================
# 🔮 ORACLE MODE
# =========================
def oracle_line(t):
    if t < 0:
        return "мир сжат в ледяной кристалл"
    if t < 10:
        return "воздух шепчет холодом"
    if t < 20:
        return "город дышит ровно"
    if t < 30:
        return "тепло усиливает пульс"
    return "жара становится доминирующей силой"


def render_oracle(w, f):
    text = f"""
🌍 {w['city']}

🔮 Оракул погоды:
— {oracle_line(w['temp'])}

🌡 Сейчас: {w['temp']}°C (ощущается {w['feels']}°C)

📜 Прогноз:
"""

    for d in f:
        text += f"— {d['day']}: {oracle_line(d['temp'])}\n"

    return text


# =========================
# 🎭 DRAMA MODE
# =========================
def render_drama(w, f):
    text = f"""
🌍 {w['city']}

⚡ Небо сегодня говорит:
Температура достигла {w['temp']}°C,
и воздух несёт {w['wind']} м/с ветра,
как дыхание невидимого существа.

"""

    for d in f:
        text += f"📅 {d['day']} — температура колеблется у {d['temp']}°C...\n"

    return text


# =========================
# 🤖 INLINE HANDLER
# =========================
async def inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.inline_query.query.strip()
    if not q:
        return

    city, mode = mode_parse(q)

    w = get_weather(city)
    f = get_forecast(city)

    if not w or not f:
        await update.inline_query.answer([
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="город не найден",
                input_message_content=InputTextMessageContent("🌪 нет данных")
            )
        ])
        return

    # =========================
    # 🎛 MODE SWITCH
    # =========================
    if mode == "oracle":
        text = render_oracle(w, f)
    elif mode == "drama":
        text = render_drama(w, f)
    else:
        text = render_science(w, f)

    result = InlineQueryResultArticle(
        id=str(uuid.uuid4()),
        title=f"{w['city']} ({mode})",
        description=f"{w['temp']}°C · {mode}",
        input_message_content=InputTextMessageContent(text)
    )

    await update.inline_query.answer([result], cache_time=10)


# =========================
# 🚀 MAIN
# =========================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_error_handler(error_handler)
    app.add_handler(InlineQueryHandler(inline))

    print("🌩 Weather Modes Bot is alive")
    app.run_polling()


if __name__ == "__main__":
    main()
