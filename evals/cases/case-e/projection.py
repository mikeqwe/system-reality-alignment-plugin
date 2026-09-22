"""A transactionally deduplicated local projection, not an external effect."""
import sqlite3


def apply(database, intent_id, payload):
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS effects (intent TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        connection.execute("INSERT OR IGNORE INTO effects VALUES (?, ?)", (intent_id, payload))
