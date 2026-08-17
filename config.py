import os

# Все секреты берутся из переменных окружения (.env), никогда не хардкодим в коде.
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHANNEL = os.environ.get("TELEGRAM_CHANNEL", "@podelukz")
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

# Каждые N минут проверяем источники
POLL_INTERVAL_MINUTES = int(os.environ.get("POLL_INTERVAL_MINUTES", "20"))

# Модель Groq (бесплатный тариф, лимит заметно выше, чем у Gemini)
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

DB_PATH = os.environ.get("DB_PATH", "posted_news.db")
REDIS_URL = os.environ["REDIS_URL"]
