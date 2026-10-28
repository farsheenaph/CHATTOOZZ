
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room as socketio_join_room

app = Flask(__name__)

app.config["SECRET_KEY"] = "chattoozzz123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chattoozz.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(50), unique=True, nullable=False)
    room_name = db.Column(db.String(100), nullable=False)
    room_password = db.Column(db.String(100), nullable=False)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/admin")
def admin():
    return render_template("admin_login.html")


@app.route("/user")
def user():
    return render_template("user_login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("admin_dashboard.html")


@app.route("/chat")
def chat():
    room_id = request.args.get("room_id", "")
    username = request.args.get("username", "Guest")

    return render_template(
        "chat.html",
        room_id=room_id,
        username=username
    )


# Let a user join their selected chat room
@socketio.on("join_chat_room")
def handle_join(data):
    room_id = str(data.get("room_id", "")).strip()
    username = str(data.get("username", "Guest")).strip()

    if not room_id:
        return

    socketio_join_room(room_id)

    emit(
        "receive_message",
        {
            "username": "CHATTOOZZ",
            "message": f"{username} joined the room."
        },
        to=room_id
    )


# Send a message to everyone in the same room
@socketio.on("send_message")
def handle_message(data):
    room_id = str(data.get("room_id", "")).strip()
    username = str(data.get("username", "Guest")).strip()
    message = str(data.get("message", "")).strip()

    if not room_id or not message:
        return

    emit(
        "receive_message",
        {
            "username": username,
            "message": message
        },
        to=room_id
    )


@app.route("/create-room")
def create_room():
    return render_template("create_room.html")


@app.route("/users")
def users():
    return "<h1>Manage Users Page</h1>"


@app.route("/history")
def history():
    return "<h1>Chat History Page</h1>"


@app.route("/save-room", methods=["POST"])
def save_room():
    room = Room(
        room_id=request.form["room_id"],
        room_name=request.form["room_name"],
        room_password=request.form["room_password"]
    )

    db.session.add(room)
    db.session.commit()

    return redirect("/rooms")


@app.route("/rooms")
def rooms():
    all_rooms = Room.query.all()
    return render_template("rooms.html", rooms=all_rooms)


@app.route("/verify-room/<int:id>", methods=["POST"])
def verify_room(id):
    room = Room.query.get_or_404(id)
    password = request.form.get("room_password", "")
    username = request.form.get("username", "Guest").strip()

    if password == room.room_password:
        if not username:
            username = "Guest"

        return redirect(url_for(
            "chat",
            room_id=room.room_id,
            username=username
        ))

    return "<h2>Invalid Room Password</h2>"


@app.route("/join-room/<int:id>")
def join_room_page(id):
    room = Room.query.get_or_404(id)
    return render_template("join_room.html", room=room)


@app.route("/delete-room/<int:id>")
def delete_room(id):
    room = Room.query.get_or_404(id)

    db.session.delete(room)
    db.session.commit()

    return redirect("/rooms")


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    socketio.run(app, debug=True)
