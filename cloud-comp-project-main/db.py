import sqlite3
import os

def get_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "data", "chords.db")
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
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progressions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progression_chords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                progression_id INTEGER NOT NULL,
                chord_id INTEGER NOT NULL,
                position INTEGER NOT NULL,
                FOREIGN KEY (progression_id) REFERENCES progressions(id),
                FOREIGN KEY (chord_id) REFERENCES chords(id)
            )
        """)

        conn.commit()
