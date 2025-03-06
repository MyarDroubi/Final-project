from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
import json
import os
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "THISISACODE"
socketio = SocketIO(app)

rooms = {}

# File to store rooms data
ROOMS_FILE = "rooms.json"

def save_rooms_to_file():
    """Save the rooms dictionary to a file."""
    with open(ROOMS_FILE, "w") as f:
        json.dump(rooms, f)

def load_rooms_from_file():
    """Load the rooms dictionary from a file."""
    global rooms
    try:
        with open(ROOMS_FILE, "r") as f:
            rooms = json.load(f)
    except FileNotFoundError:
        rooms = {}  # If the file doesn't exist, start with an empty dictionary

load_rooms_from_file()


def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    return code

# Routes för vanliga webbsidor
@app.route('/')
def index():
    return render_template('Index.html')

@app.route('/livechats')
def livechats():
    return render_template('Livechats.html')

@app.route('/kontakt')
def kontakt():
    return render_template('Kontakt.html')

@app.route('/om_oss')
def om_oss():
    return render_template('Om_oss.html')

@app.route('/inloggning')
def inloggning():
    return render_template('Inloggning.html')

@app.route("/home", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        subject = request.form.get("subject")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if create and not subject:
            return render_template("home.html", error="Please enter a Subject!", code=code, name=name, subject=subject)

        if join != False and not code:
            return render_template("home.html", error="Please enter a room Code", code=code, name=name, subject=subject)

        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": [], "subject": subject, "creator": name}
            save_rooms_to_file()  # Save rooms to file after creating a new room
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist", code=code, name=name, subject=subject)

        session["room"] = room
        session["name"] = name
        session["subject"] = subject
        return redirect(url_for("room"))

    return render_template("home.html")
    
@app.route("/room")
def room():
    room = session.get("room")
    name = session.get("name")
    subject = session.get("subject")

    if room is None or name is None or room not in rooms or subject is None:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"], name=name, subject=subject)


@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return
    content = {
        "name": session.get("name"),
        "subject": session.get("subject"),  # Lägg till subject
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} (Subject: {session.get('subject')}) said: {data['data']}")


@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    subject = session.get("subject")  # Tillagt

    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    join_room(room)
    send({"name": name, "subject": subject, "message": "has entered the room"}, to=room)  # subject tillagt
    rooms[room]["members"] += 1
    print(F"{name} (Subject: {subject}) joined room {room}")  # subject tillagt

@app.route("/show_rooms")
def show_rooms():
    # Load rooms from file to ensure we have the latest data
    load_rooms_from_file()
    return render_template("show_rooms.html", rooms=rooms)

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -=1
        if rooms[room]["members"] <=0:
            del rooms[room]
    send({"name": name, "message": "has left the room"}, to=room)
    print(F"{name} has left the room {room}")



if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=8888)
