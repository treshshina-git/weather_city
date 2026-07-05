def oracle(t):
    if t < 0:
        return "мир сжат в ледяной кристалл"
    if t < 10:
        return "воздух шепчет холодом"
    if t < 20:
        return "город дышит ровно"
    if t < 30:
        return "тепло усиливает пульс"
    return "жара становится доминирующей силой"


def scientific(w):
    return f"""
🌍 <b>{w['city']}</b>
🕒 Сейчас: <b>{city_time(w['timezone'])}</b>
🌅 Рассвет: <b>{city_time(w['sunrise'])}</b>
🌇 Закат: <b>{city_time(w['sunset'])}</b>
🌡 Температура: <b>{w['temp']}°C</b>
🫧 Ощущается: <b>{w['feels']}°C</b>
💨 Ветер: <b>{w['wind']} м/с</b>
🧭 Давление: <b>{w['pressure']} hPa</b>
💧 Влажность: <b>{w['humidity']}%</b>
"""


def drama(w):
    return f"""
⚡ {w['city']} сегодня под давлением стихии

Температура: {w['temp']}°C
Ветер: {w['wind']} м/с

Небо ведёт себя как живой организм.
"""
