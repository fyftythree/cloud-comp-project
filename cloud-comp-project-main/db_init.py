from models import insert_chord, notes, types, intervals, insert_chord_note
from db import init_db
from db import get_connection

init_db()

chords = [(note, t) for note in notes for t in types]

def init_chords():
    for note in notes:
        for t in types:
            insert_chord(note, t)

def build_chord(root, chord_type): #helper for init_chord_notes

    root_index = notes.index(root)
    chord_notes = []

    for note in intervals[chord_type]:
        chord_notes.append(notes[(root_index + note) % len(notes)]) #starting from the root, goes through notes and adds according to intervals

    return chord_notes

def init_chord_notes():
    with get_connection() as conn:
        cursor = conn.cursor()

        for n in notes:
            for t in types:
                #get the chord id
                cursor.execute("""
                    SELECT id
                    FROM chords 
                    WHERE name = ? AND type = ?
                """,(n,t))

                result = cursor.fetchone()
                if result is None:
                    continue

                chord_id = result[0]
                chord_notes = build_chord(n,t)

                for note in chord_notes:
                    insert_chord_note(cursor, chord_id, note)



if __name__ == '__main__':
    init_chords()
    init_chord_notes()
    print("Database initialized")