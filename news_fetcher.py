import logging
import feedparser
from sources import RSS_FEEDS

logger = logging.getLogger(__name__)


def fetch_latest_articles():
    """
    Проходит по всем RSS-источникам, возвращает список статей.
    Каждая статья: {title, link, summary, image_url, source}
    Если один источник упал — просто пропускаем его, остальные работают.
    """
    articles = []

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            if feed.bozo and not feed.entries:
                logger.warning(f"Источник не отдал данных: {feed_url}")
                continue

            source_name = feed.feed.get("title", feed_url)

            for entry in feed.entries[:10]:  # берём последние 10 из каждой ленты
                image_url = _extract_image(entry)
                articles.append({
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", "").strip(),
                    "summary": _clean_summary(entry.get("summary", "")),
                    "image_url": image_url,
                    "source": source_name,
                })
        except Exception as e:
            logger.warning(f"Ошибка при чтении {feed_url}: {e}")
            continue

    return articles


def _extract_image(entry):
    # Пробуем разные места, где RSS обычно прячет картинку
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
