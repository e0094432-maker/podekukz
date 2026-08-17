import logging
import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL

logger = logging.getLogger(__name__)

API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def post_to_channel(text, image_url=None, source_link=None):
    """
    Публикует пост в канал. Если есть картинка — фото с подписью,
    иначе просто текст. В конце добавляем ссылку на источник.
    """
    full_text = text
    if source_link:
        full_text += f"\n\n🔗 Источник: {source_link}"

    try:
        if image_url:
            # Telegram ограничивает подпись к фото 1024 символами
            caption = full_text[:1024]
            resp = requests.post(
                f"{API_BASE}/sendPhoto",
                data={
                    "chat_id": TELEGRAM_CHANNEL,
                    "photo": image_url,
                    "caption": caption,
                },
                timeout=30,
            )
            if resp.status_code != 200:
                logger.warning(f"sendPhoto не сработал ({resp.text}), пробуем без фото")
                return _send_text(full_text)
            return True
        else:
            return _send_text(full_text)
    except Exception as e:
        logger.error(f"Ошибка публикации в Telegram: {e}")
        return False


def _send_text(text):
    resp = requests.post(
        f"{API_BASE}/sendMessage",
        data={"chat_id": TELEGRAM_CHANNEL, "text": text[:4096]},
        timeout=30,
    )
    if resp.status_code != 200:
        logger.error(f"sendMessage провалился: {resp.text}")
        return False
    return True
