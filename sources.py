# Список RSS-фидов казахстанских новостных сайтов.
# Проверенные рабочие фиды. Если сайт отдаёт ошибку — парсер просто
# пропускает его в этом цикле (см. news_fetcher.py), остальные источники
# продолжают работать.
#
# Добавить свой источник — просто впиши новую строку с URL RSS-ленты.

RSS_FEEDS = [
    "https://astanatimes.com/feed/atom/",   # The Astana Times
    "https://time.kz/rss",                   # Time.kz
    "https://liter.kz/feed/",                # Liter.kz
    # Ниже — источники без официального публичного RSS на момент проверки.
    # Если у тебя есть их RSS-ссылки (или ты найдёшь актуальные) — добавь сюда:
    # "https://tengrinews.kz/rss/news.xml",
    # "https://informburo.kz/rss",
    # "https://www.zakon.kz/rss",
]
