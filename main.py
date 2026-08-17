import logging
import time

from config import POLL_INTERVAL_MINUTES
from db import init_db, already_posted, mark_posted
from news_fetcher import fetch_latest_articles
from generator import generate_post
from poster import post_to_channel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run_cycle():
    articles = fetch_latest_articles()
    logger.info(f"Найдено статей в источниках: {len(articles)}")

    new_count = 0
    for article in articles:
        if not article["title"] or not article["link"]:
            continue
        if already_posted(article):
            continue

        logger.info(f"Новая статья: {article['title']} ({article['source']})")

        post_text = generate_post(article)
        if not post_text:
            logger.warning("Не удалось сгенерировать пост, пропускаем статью")
            continue

        ok = post_to_channel(
            text=post_text,
            image_url=article.get("image_url"),
            source_link=article["link"],
        )
        if ok:
            mark_posted(article)
            new_count += 1
            logger.info("Опубликовано.")
            # небольшая пауза между постами, чтобы не спамить канал разом
            time.sleep(15)
        else:
            logger.error("Публикация не удалась, статья НЕ помечена как опубликованная")

    logger.info(f"Цикл завершён. Опубликовано новых постов: {new_count}")


def main():
    init_db()
    logger.info("Бот запущен. Проверка новостей каждые %s мин.", POLL_INTERVAL_MINUTES)
    while True:
        try:
            run_cycle()
        except Exception as e:
            logger.error(f"Ошибка в цикле: {e}")
        time.sleep(POLL_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main()
