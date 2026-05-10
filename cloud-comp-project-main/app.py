from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
from models import *
import bcrypt
import time

app = Flask(__name__)
CORS(app)
app.secret_key = "dev-secret-key"

@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/chord_page")
def chord_page():
    if "user_id" not in session:
        return redirect("/login")

    progressions = get_user_progressions(session["user_id"])

    return render_template(
        "index.html",
        progressions=progressions
    )

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("dashboard.html", username=session["username"])

@app.route("/progressions")
def progressions_page():
    if "user_id" not in session:
        return redirect("/login")

    progressions = get_user_progressions(session["user_id"])

    return render_template(
        "progressions.html",
        username=session["username"],
        progressions=progressions
    )

@app.route("/validate_progression", methods=["POST"])
def validate_progression():
    if "user_id" not in session:
        return {"valid": False, "error": "User not logged in"}, 401

    name = request.json.get("name")

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM progressions,
            WHERE user_id=? AND name=?
        """, (session["user_id"], name))

        result = cursor.fetchone()

        if result:
            return {"valid": True}
        else:
            return {"valid": False, "error": "Progression does not exist"}

@app.route("/create_progression", methods=["POST"])
def create_progression():
    if "user_id" not in session:
        return redirect("/login")

    name = request.form["name"]

    create_progression_db(session["user_id"], name)

    return redirect("/progressions")

@app.route("/progression/<int:progression_id>")
def view_progression(progression_id):
    if "user_id" not in session:
        return redirect("/login")

    progression = get_progression(progression_id, session["user_id"])
    chords = get_progression_chord_notes(progression_id)

    return render_template(
        "progression_view.html",
        progression=progression,
        chords=chords
    )

@app.route("/api/add_to_progression", methods=["POST"])
def add_to_progression():
    if "user_id" not in session:
        return {"error": "Not logged in"}, 401

    data = request.get_json()

    progression_id = data["progression_id"]
    chord_name = data["chord_name"]
    chord_type = data["chord_type"]

    progression = get_progression(progression_id, session["user_id"])
    if not progression:
        return {"error": "Progression not found"}

    chord = get_user_chord(chord_name, chord_type)
    if not chord:
        return {"error": "Chord not found"}

    add_chord_to_progression(progression[0], chord[0])

    return {"success": True}

@app.route('/api/chord')
def get_chord():
    name = request.args.get("name")
    chord_type = request.args.get("type")

    notes = get_chord_note(name, chord_type)

    return jsonify({"notes": notes})

@app.route("/api/create_account", methods=["POST"])
def create_account():
    username = request.form["username"]
    password = request.form["password"]

    register_success = create_user(username, password)

    if register_success:
        create_user(username, password)
        return redirect("/login")
    else:
        return render_template("login.html", error="User already exists")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = verify_user(username, password)

        if user_id:
            session["user_id"] = user_id
            session["username"] = username

            return redirect("/dashboard")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/delete_progression/<int:id>", methods=["POST"])
def delete_progression(id):

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    conn = sqlite3.connect("data/chords.db")
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM progression_chords
        WHERE progression_id = ?
    """, (id,))

    cursor.execute("""
        DELETE FROM progressions
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()

    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


