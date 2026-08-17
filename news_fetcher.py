import logging
import time
from calendar import timegm
from datetime import datetime, timezone

import feedparser
from sources import RSS_FEEDS

logger = logging.getLogger(__name__)

# Не постим статьи старше этого срока — иначе при каждом перезапуске
# или сбое бот начинает выкладывать вчерашние/недельные новости как свежие.
MAX_ARTICLE_AGE_HOURS = 48


def fetch_latest_articles():
    """
    Проходит по всем RSS-источникам, возвращает список СВЕЖИХ статей
    (не старше MAX_ARTICLE_AGE_HOURS).
    Каждая статья: {title, link, summary, image_url, source, source_type}
    Если один источник упал — просто пропускаем его, остальные работают.
    """
    articles = []
    now_ts = time.time()

    for feed_cfg in RSS_FEEDS:
        feed_url = feed_cfg["url"]
        source_type = feed_cfg.get("type", "news")
        try:
            feed = feedparser.parse(feed_url)
            if feed.bozo and not feed.entries:
                logger.warning(f"Источник не отдал данных: {feed_url}")
                continue

            source_name = feed.feed.get("title", feed_url)

            for entry in feed.entries[:15]:
                published_ts = _entry_timestamp(entry)

                # Если у записи вообще нет даты — не рискуем, пропускаем её,
                # чтобы не запостить неизвестно что как "свежее".
                if published_ts is None:
                    continue

                age_hours = (now_ts - published_ts) / 3600
                if age_hours > MAX_ARTICLE_AGE_HOURS:
                    continue

                image_url = _extract_image(entry)
                articles.append({
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", "").strip(),
                    "summary": _clean_summary(entry.get("summary", "")),
                    "image_url": image_url,
                    "source": source_name,
                    "source_type": source_type,
                    "published_ts": published_ts,
                })
        except Exception as e:
            logger.warning(f"Ошибка при чтении {feed_url}: {e}")
            continue

    # Свежее — вперёд
    articles.sort(key=lambda a: a["published_ts"], reverse=True)
    return articles


def _entry_timestamp(entry):
    # feedparser кладёт распарсенную дату в published_parsed/updated_parsed
    # (struct_time в UTC). Берём что есть.
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
