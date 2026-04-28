import sqlite3
from db import get_connection
import bcrypt
import time

notes = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
types = ["major", "minor", "augmented", "diminished"]
intervals = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "augmented": [0, 4, 8],
    "diminished": [0, 3, 6]
}

def insert_chord(name, chord_type):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO chords (name, type)
            VALUES (?, ?)
        """, (name, chord_type))

def get_chord(name, chord_type):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM chords WHERE name = ?
            AND type = ?
        """, (name, chord_type))
        return cursor.fetchone()

def insert_chord_note(cursor, chord_id, note):
    cursor.execute("""
        INSERT OR IGNORE INTO chord_notes (chord_id, note)
        VALUES (?, ?)
    """,(chord_id, note))

def get_chord_note(name, chord_type):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cn.note
            FROM chord_notes cn
            JOIN chords c ON cn.chord_id = c.id
            WHERE c.name = ? AND c.type = ?
        """, (name, chord_type))
        return [row[0] for row in cursor.fetchall()]

def create_user(username, password):

    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    with get_connection() as conn:
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
            """, (username, hashed))

            conn.commit()
            return cursor.lastrowid

        except:
            conn.rollback()

def verify_user(username, password):
    password_bytes = password.encode("utf-8")

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, password_hash
            FROM users
            WHERE username = ?
        """, (username, ))

        user = cursor.fetchone()

        if not user:
            return None

        user_id, stored_hash = user

        if bcrypt.checkpw(password_bytes, stored_hash):
            return user_id

        return None