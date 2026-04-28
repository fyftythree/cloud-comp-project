import sqlite3

db_path = "./data/chords.db"

def get_connection():
    return sqlite3.connect(db_path)

def init_db():
    with sqlite3.connect("./data/chords.db") as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                UNIQUE (name,type)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chord_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chord_id INTEGER NOT NULL,
                note TEXT NOT NULL,
                FOREIGN KEY (chord_id) REFERENCES chords (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        conn.commit()
