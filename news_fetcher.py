import logging
import time
from calendar import timegm

import feedparser
from sources import RSS_FEEDS

logger = logging.getLogger(__name__)

# Не постим статьи старше этого срока — иначе при каждом перезапуске
# (а на бесплатном хостинге база дедупликации не сохраняется между
# перезапусками) бот начинает выкладывать вчерашние новости как свежие.
MAX_ARTICLE_AGE_HOURS = 8

# Слова-маркеры, по которым определяем, что новость про закон/поправки —
# для таких новостей комментарий строится по-другому (см. generator.py).
LEGAL_KEYWORDS = [
    "закон", "поправк", "изменени", "кодекс", "законопроект",
    "подписал указ", "вступ", "штраф", "льгот", "выплат",
]


def fetch_latest_articles():
    """
    Проходит по всем RSS-источникам, возвращает список СВЕЖИХ статей
    (не старше MAX_ARTICLE_AGE_HOURS), отсортированных от новых к старым.
    Каждая статья: {title, link, summary, image_url, source, is_legal}
    Если один источник упал — просто пропускаем его, остальные работают.
    """
    articles = []
    now_ts = time.time()

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            if feed.bozo and not feed.entries:
                logger.warning(f"Источник не отдал данных: {feed_url}")
                continue

            source_name = feed.feed.get("title", feed_url)

            for entry in feed.entries[:15]:
                published_ts = _entry_timestamp(entry)
                if published_ts is None:
                    continue

                age_hours = (now_ts - published_ts) / 3600
                if age_hours > MAX_ARTICLE_AGE_HOURS:
                    continue

                title = entry.get("title", "").strip()
                summary = _clean_summary(entry.get("summary", ""))

                articles.append({
                    "title": title,
                    "link": entry.get("link", "").strip(),
                    "summary": summary,
                    "image_url": _extract_image(entry),
                    "source": source_name,
                    "is_legal": _looks_legal(title, summary),
                    "published_ts": published_ts,
                })
        except Exception as e:
            logger.warning(f"Ошибка при чтении {feed_url}: {e}")
            continue

    articles.sort(key=lambda a: a["published_ts"], reverse=True)
    return articles


def _looks_legal(title, summary):
    text = f"{title} {summary}".lower()
    return any(kw in text for kw in LEGAL_KEYWORDS)


def _entry_timestamp(entry):
    for field in ("published_parsed", "updated_parsed"):
        value = entry.get(field)
        if value:
            try:
                return timegm(value)
            except Exception:
                continue
    return None


def _extract_image(entry):
    if "media_content" in entry and entry.media_content:
        return entry.media_content[0].get("url")
    if "media_thumbnail" in entry and entry.media_thumbnail:
        return entry.media_thumbnail[0].get("url")
    if "links" in entry:
        for link in entry.links:
            if link.get("type", "").startswith("image/"):
                return link.get("href")
    return None


def _clean_summary(raw_html):
    import re
    text = re.sub("<[^<]+?>", "", raw_html or "")
    return text.strip()
