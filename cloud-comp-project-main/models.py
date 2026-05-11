import sqlite3
import psycopg2
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
            INSERT INTO chords (name, type)
            VALUES (%s, %s)
            ON CONFLICT (name, type) DO NOTHING
        """, (name, chord_type))

        conn.commit()

def get_user_chord(name, chord_type):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM chords
            WHERE name = %s AND type = %s
        """, (name, chord_type))

        return cursor.fetchone()

def insert_chord_note(cursor, chord_id, note):
    cursor.execute("""
        INSERT INTO chord_notes (chord_id, note)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """, (chord_id, note))

def get_chord_note(name, chord_type):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cn.note
            FROM chord_notes cn
            JOIN chords c ON cn.chord_id = c.id
            WHERE c.name = %s AND c.type = %s
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
                VALUES (%s, %s)
            """, (username, hashed))

            conn.commit()
            return True

        except:
            conn.rollback()
            return False

def verify_user(username, password):
    password_bytes = password.encode("utf-8")

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, password_hash
            FROM users
            WHERE username = %s
        """, (username,))

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
            WHERE user_id = %s 
        """, (user_id,))

        return cursor.fetchall()

def get_progression(progression_id, user_id): #for one specific progression
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name
            FROM progressions
            WHERE id = %s AND user_id = %s
        """, (progression_id, user_id))

        return cursor.fetchone()

def get_progression_chords(progression_id): # get each chord in a progression using ids
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.name, c.type, STRING_AGG(n.note, ',')
            FROM progression_chords pc
            JOIN chords c ON pc.chord_id = c.id
            JOIN chord_notes n ON c.id = n.chord_id
            WHERE pc.progression_id = %s
            GROUP BY pc.id, c.name, c.type
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
                STRING_AGG(n.note, ',')
            FROM progression_chords pc
            JOIN chords c ON pc.chord_id = c.id
            JOIN chord_notes n ON c.id = n.chord_id
            WHERE pc.progression_id = %s
            GROUP BY pc.id, pc.position, c.name, c.type
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
            VALUES (%s, %s)
        """, (user_id, name))

        conn.commit()

def add_chord_to_progression(progression_id, chord_id):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM progression_chords
            WHERE progression_id = %s
        """, (progression_id,))

        position = cursor.fetchone()[0] + 1

        cursor.execute("""
            INSERT INTO progression_chords (progression_id, chord_id, position)
            VALUES (%s, %s, %s)
        """, (progression_id, chord_id, position))

        conn.commit()