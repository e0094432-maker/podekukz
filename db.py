import sqlite3
import hashlib
from config import DB_PATH


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS posted (
            hash TEXT PRIMARY KEY,
            link TEXT,
            title TEXT,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def _hash_article(article):
    key = (article.get("link") or article.get("title") or "").strip().lower()
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def already_posted(article):
    conn = sqlite3.connect(DB_PATH)
    h = _hash_article(article)
    row = conn.execute("SELECT 1 FROM posted WHERE hash = ?", (h,)).fetchone()
    conn.close()
    return row is not None


def mark_posted(article):
    conn = sqlite3.connect(DB_PATH)
    h = _hash_article(article)
    conn.execute(
        "INSERT OR IGNORE INTO posted (hash, link, title) VALUES (?, ?, ?)",
        (h, article.get("link"), article.get("title")),
    )
    conn.commit()
    conn.close()
