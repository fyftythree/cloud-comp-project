import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432)
    )

def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chords (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            UNIQUE (name, type)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chord_notes (
            id SERIAL PRIMARY KEY,
            chord_id INTEGER NOT NULL,
            note TEXT NOT NULL,
            FOREIGN KEY (chord_id) REFERENCES chords (id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progressions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progression_chords (
            id SERIAL PRIMARY KEY,
            progression_id INTEGER NOT NULL,
            chord_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            FOREIGN KEY (progression_id) REFERENCES progressions(id) ON DELETE CASCADE,
            FOREIGN KEY (chord_id) REFERENCES chords(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
