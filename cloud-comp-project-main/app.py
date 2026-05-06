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
        return redirect("/chord_page")
    return redirect("/login")


@app.route('/chord_page')
def chord():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("index.html", username=session.get("username"))

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

            return redirect("/chord_page")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html", username=session.get("username"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == '__main__':
    app.run(debug=True)
