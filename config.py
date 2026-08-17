import os

# Все секреты берутся из переменных окружения (.env), никогда не хардкодим в коде.
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHANNEL = os.environ.get("TELEGRAM_CHANNEL", "@podelukz")
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# Каждые N минут проверяем источники
POLL_INTERVAL_MINUTES = int(os.environ.get("POLL_INTERVAL_MINUTES", "20"))

# Модель Gemini (бесплатный тариф)
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

DB_PATH = os.environ.get("DB_PATH", "posted_news.db")
