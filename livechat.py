from flask import Flask, render_template, request, session, redirect, url_for, flash, g
from flask_socketio import join_room, leave_room, send, SocketIO
import random
import json
import os
from string import ascii_uppercase
from huggingface_hub import InferenceClient
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta


app = Flask(__name__)
app.config["SECRET_KEY"] = "THISISACODE"
socketio = SocketIO(app)

# Initialize the bot client
bot_client = InferenceClient(
    provider="novita",
    api_key="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"
)

# SQLite Database Setup
DATABASE = "users.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db_connection()
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        db.commit()
        db.close()

init_db()

rooms = {}
ROOMS_FILE = "rooms.json"

def save_rooms_to_file():
    """Save the rooms dictionary to a file."""
    with open(ROOMS_FILE, "w") as f:
        json.dump(rooms, f)

def clear_and_save_rooms_to_file():
    """Clear the file and save the updated rooms dictionary."""
    with open(ROOMS_FILE, "w") as f:
        json.dump({}, f)  # Rensa filen genom att skriva en tom dictionary
    save_rooms_to_file()  # Spara den uppdaterade datastrukturen

def load_rooms_from_file():
    """Load the rooms dictionary from a file."""
    global rooms
    try:
        # Check if the file exists and is not empty
        if os.path.exists(ROOMS_FILE) and os.path.getsize(ROOMS_FILE) > 0:
            with open(ROOMS_FILE, "r") as f:
                rooms = json.load(f)
        else:
            rooms = {}  # If the file doesn't exist or is empty, start with an empty dictionary
    except json.JSONDecodeError:
        print("Error: Invalid JSON in rooms file. Initializing with an empty dictionary.")
        rooms = {}  # If the JSON is invalid, start with an empty dictionary
    except Exception as e:
        print(f"Error loading rooms from file: {e}")
        rooms = {}  # If any other error occurs, start with an empty dictionary

# Clear rooms when the server starts
clear_and_save_rooms_to_file()

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break
    return code

def bot_interaction(room, user_message=None):
    """Bot interacts if there is only one person in the room."""
    if rooms[room]["members"] == 1:
        if user_message:
            # Generate a response to the user's message
            messages = [
                {"role": "user", "content": user_message}
            ]
            
            completion = bot_client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
                messages=messages,
                max_tokens=500,
            )
            bot_response = completion.choices[0].message.content

            # Extract the part after </think>
            if "</think>" in bot_response:
                final_answer = bot_response.split("</think>")[-1].strip()  # Get everything after </think>
            else:
                final_answer = bot_response  # Fallback if </think> is not found

        else:
            # Send a greeting if no user message is provided
            final_answer = "Hello! I'm your chat companion. What would you like to talk about?"

        # Send the bot's response to the room
        send({"name": "Bot", "message": final_answer}, to=room)
        rooms[room]["messages"].append({"name": "Bot", "message": final_answer})

@app.before_request
def load_logged_in_user():
    g.user = None
    if 'user_id' in session:
        g.user = session['user_id']

# Routes
@app.route("/", methods=["GET", "POST"])
def inloggning():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("E-postadress och lösenord krävs!", "error")
            return redirect(url_for("inloggning"))

        db = get_db_connection()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        db.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            
            # Gör sessionen permanent (upphör inte när webbläsaren stängs)
            session.permanent = True
            app.permanent_session_lifetime = timedelta(days=30)  # Sätt en längre livslängd (t.ex. 30 dagar)

            return redirect(url_for("index"))  # Omdirigera till hem efter lyckad inloggning
        else:
            flash("Fel e-postadress eller lösenord!", "error")
            return redirect(url_for("inloggning"))  # Omdirigera tillbaka till inloggningssidan vid fel
        

    return render_template("Inloggning.html")

@app.route('/index')
def index():
    if "user_id" not in session:
        flash("Vänligen logga in för att komma åt denna sida.", "error")
        return redirect(url_for("inloggning"))
    return render_template('Index.html')

@app.route('/om_oss')
def om_oss():
    if "user_id" not in session:
        flash("Vänligen logga in för att komma åt denna sida.", "error")
        return redirect(url_for("inloggning"))
    return render_template('Om_oss.html')



# Signup Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if  not email or not password:
            flash("e-post och lösenord krävs!", "error")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)

        try:
            db = get_db_connection()
            db.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
            db.commit()
            db.close()
            flash("Kontot har skapats! Vänligen logga in.", "success")
            return redirect(url_for("inloggning"))
        except sqlite3.IntegrityError:
            flash("E-postadressen finns redan!", "error")
            return redirect(url_for("signup"))

    return render_template("signup.html")

# Logout Route
@app.route("/logout")
def logout():
    session.clear()
    flash("Du har loggat ut.", "success")
    return redirect(url_for("inloggning"))

@app.route("/home", methods=["POST", "GET"])
def home():
    if "user_id" not in session:
        flash("Vänligen logga in för att komma åt denna sida.", "error")
        return redirect(url_for("inloggning"))

    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        subject = request.form.get("subject")
        join = request.form.get("join", False)
        create = request.form.get("create", False)
        
        if create and not subject.strip():
            return render_template("home.html", error="Please enter a Subject!", code=code, name=name, subject=subject, rooms=rooms)

        if join != False and not code:
            return render_template("home.html", error="Please enter a room Code", code=code, name=name, subject=subject, rooms=rooms)

        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": [], "subject": subject, "creator": name}
            save_rooms_to_file()
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist", code=code, name=name, subject=subject, rooms=rooms)
        else:
            # Hämta ämnet från det befintliga rummet när man ansluter
            subject = rooms[code]["subject"]

        session["room"] = room
        session["name"] = name
        session["subject"] = subject  # Spara ämnet i sessionen även när man ansluter
        return redirect(url_for("room"))

    return render_template("home.html", rooms=rooms)

@app.route("/room")
def room():
    room = session.get("room")
    name = session.get("name")
    subject = session.get("subject")

    if room is None or name is None or room not in rooms or subject is None:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"], name=name, subject=subject)

# SocketIO Events
@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return
    content = {
        "name": session.get("name"),
        "subject": session.get("subject"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} (Subject: {session.get('subject')}) said: {data['data']}")

    # Check if the bot should interact
    bot_interaction(room, user_message=data["data"])

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    subject = session.get("subject")

    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    join_room(room)
    send({"name": name, "subject": subject, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} (Subject: {subject}) joined room {room}")

    # Check if the bot should interact
    bot_interaction(room)

@app.route("/show_rooms")
def show_rooms():
    load_rooms_from_file()
    return render_template("show_rooms.html", rooms=rooms)

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
            clear_and_save_rooms_to_file()

    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

if __name__ == "__main__":
    socketio.run(app, debug=True)