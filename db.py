import hashlib
import logging
import redis

from config import REDIS_URL

logger = logging.getLogger(__name__)

# Отдельный сервис Redis на Render — не стирается при передеплое бота,
# в отличие от локального файла на бесплатном Web Service.
_client = redis.from_url(REDIS_URL, decode_responses=True)

POSTED_SET_KEY = "podelukz:posted_hashes"


def init_db():
    # Redis ничего не нужно создавать заранее — просто проверим соединение.
    try:
        _client.ping()
        logger.info("Соединение с Redis установлено.")
    except Exception as e:
        logger.error(f"Не удалось подключиться к Redis: {e}")
        raise


def _hash_article(article):
    key = (article.get("link") or article.get("title") or "").strip().lower()
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def already_posted(article):
    h = _hash_article(article)
    return bool(_client.sismember(POSTED_SET_KEY, h))


def mark_posted(article):
    h = _hash_article(article)
    _client.sadd(POSTED_SET_KEY, h)
