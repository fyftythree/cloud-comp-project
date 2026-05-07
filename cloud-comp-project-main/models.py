import sqlite3
from db import get_connection
import bcrypt
import time

notes = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
types = ["maj", "min", "aug", "dim", "maj7", "7", "min7", "9", "add9"]
intervals = {
    "maj":   [0, 4, 7],
    "min":   [0, 3, 7],
    "aug":   [0, 4, 8],
    "dim":   [0, 3, 6],
    "maj7":  [0, 4, 7, 11],
    "7":     [0, 4, 7, 10],
    "min7":  [0, 3, 7, 10],
    "9":     [0, 4, 7, 10, 14],
    "add9":  [0, 4, 7, 14]
}

def insert_chord(name, chord_type):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO chords (name, type)
            VALUES (?, ?)
        """, (name, chord_type))

def get_user_chord(name, chord_type):
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

def get_user_progressions(user_id): #for ALL progressions
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name
            FROM progressions
            WHERE user_id = ?
        """, (user_id,))

        return cursor.fetchall()

def get_progression(progression_id, user_id): #for one specific progression
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name
            FROM progressions
            WHERE id = ? AND user_id = ?
        """, (progression_id, user_id))

        return cursor.fetchone()

def get_progression_chords(progression_id): #get each chord from one progression using id
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.name, c.type, GROUP_CONCAT(n.note)
            FROM progression_chords pc
            JOIN chords c ON pc.chord_id = c.id
            JOIN chord_notes n ON c.id = n.chord_id
            WHERE pc.progression_id = ?
            GROUP BY pc.id
            ORDER BY pc.position
        """, (progression_id,))

        return cursor.fetchall()

def get_progression_chord_notes(progression_id):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
                pc.position,
                c.name,
                c.type,
                GROUP_CONCAT(n.note)
            FROM progression_chords pc
            JOIN chords c ON pc.chord_id = c.id
            JOIN chord_notes n ON c.id = n.chord_id
            WHERE pc.progression_id = ?
            GROUP BY pc.id
            ORDER BY pc.position
        """, (progression_id,))

        rows = cursor.fetchall()

        chords = []

        for row in rows:
            position, name, chord_type, chord_notes = row
            chords.append({
                "position": position,
                "name": name,
                "type": chord_type,
                "notes": chord_notes.split(",")
            })

        return chords
        

def create_progression_db(user_id, name):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO progressions (user_id, name)
            VALUES (?, ?)
        """, (user_id, name))

        conn.commit()

def add_chord_to_progression(progression_id, chord_id):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM progression_chords
            WHERE progression_id = ?
        """, (progression_id,))

        position = cursor.fetchone()[0] + 1

        cursor.execute("""
            INSERT INTO progression_chords (progression_id, chord_id, position)
            VALUES (?, ?, ?)
        """, (progression_id, chord_id, position))

        conn.commit()