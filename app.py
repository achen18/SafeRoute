from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    make_response
)

from flask_socketio import (
    SocketIO,
    emit
)

import json
import eventlet
eventlet.monkey_patch()

# Import login and database functions
from login import (
    database_init,
    user_register,
    user_login,
    get_user_profile
)

# Import  Redis session management 
from session_manager import (
    login_user,
    logout_user,
    current_user,
    logged_in
)

# Import pathfinding algorithm functions
from astar_utils import (
    astar,
    polygon_to_cells,
    GRID_ROWS,
    GRID_COLS
)

app = Flask(__name__)
app.secret_key = "saferoute_secret"

# Init Socket.io network handler engine
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="eventlet"
)

# Initialize SQLite tables
database_init()

# Load floorplan layout dimensions
with open("saved_floorplans.json", "r") as f:
    floorplans = json.load(f)

live_zones = {}

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    # database authentication check
    userid = user_login(username, password)

    if userid is None:
        return render_template(
            "login.html",
            error="Invalid credentials"
        )

    profile = get_user_profile(username)

    # start UUID session inside Redis server
    login_user({
        "userid": userid,
        "username": username,
        "role": profile["role"]
    })

    if profile["role"] == "admin":
        return redirect("/teacher")

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form["username"]
    password = request.form["password"]
    fname = request.form["fname"]
    lname = request.form["lname"]
    role = request.form["role"]

    userid = user_register(username, password, role, fname, lname)

    if userid == -1:
        return render_template(
            "register.html",
            error="Username taken"
        )

    return redirect("/login")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


@app.route("/")
def student():
    if not logged_in():
        return redirect("/login")

    if current_user()["role"] == "admin":
        return redirect("/teacher")

    return render_template(
        "student.html",
        profile=current_user()
    )


@app.route("/teacher")
def teacher():
    if not logged_in():
        return redirect("/login")

    if current_user()["role"] != "admin":
        return redirect("/")

    return render_template(
        "teacher.html",
        profile=current_user()
    )


@app.route("/floorplans")
def get_floorplans():
    return jsonify(floorplans)


@app.route("/route", methods=["POST"])
def route():
    data = request.json
    building = data["building"]
    start = tuple(data["start"])

    fp = next(f for f in floorplans if f["name"] == building)
    walls = set(tuple(x) for x in fp["walls"])
    exits = [tuple(x) for x in fp["exits"]]

    danger = set()
    safe = set()

    if building in live_zones:
        for zone in live_zones[building]:
            cells = polygon_to_cells(zone["points"])
            if zone["type"] == "danger":
                danger.update(cells)
            if zone["type"] == "safe":
                safe.update(cells)

    best_path = []

    for ex in exits:
        path = astar(start, ex, walls, danger, safe)
        if path and (not best_path or len(path) < len(best_path)):
            best_path = path

    return jsonify(best_path)


@app.route("/zones")
def get_zones():
    return jsonify(live_zones)


@socketio.on("zone_update")
def zone_update(data):
    print("ZONE RECEIVED VIA SOCKET")
    building = data["building"]

    if building not in live_zones:
        live_zones[building] = []

    live_zones[building].append(data)

    socketio.emit("zone_sync", data)


if __name__ == "__main__":
    socketio.run(
        app,
        debug=True,
        port=5050
    )