from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit

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
@socketio.on("send_message")
def handle_message(message):
    emit("receive_message", message, broadcast=True)

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
    return render_template("chat.html")
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
    print("Room created successfully!")

    return redirect("/rooms")
@app.route("/rooms")
def rooms():

    all_rooms = Room.query.all()

    return render_template("rooms.html", rooms=all_rooms)
@app.route("/verify-room/<int:id>", methods=["POST"])
def verify_room(id):

    room = Room.query.get_or_404(id)

    password = request.form["room_password"]

    if password == room.room_password:

        return redirect("/chat")

    else:

        return "<h2>Invalid Room Password</h2>"
@app.route("/join-room/<int:id>")
def join_room(id):

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
