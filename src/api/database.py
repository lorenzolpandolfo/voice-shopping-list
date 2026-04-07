import sqlite3

DB_NAME = "voice_shopping_list.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)

    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA temp_store=MEMORY;")
    conn.execute("PRAGMA cache_size=-8000;")
    conn.execute("PRAGMA foreign_keys=ON;")

    return conn
