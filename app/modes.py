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
🌍 {w['city']}
🌡 {w['temp']}°C (ощущается {w['feels']}°C)
💨 {w['wind']} m/s
🧭 {w['pressure']} hPa
"""


def drama(w):
    return f"""
⚡ {w['city']} сегодня под давлением стихии

Температура: {w['temp']}°C
Ветер: {w['wind']} м/с

Небо ведёт себя как живой организм.
"""