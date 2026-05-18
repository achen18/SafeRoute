# =========================
# app.py
# =========================

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect
)

from flask_socketio import (
    SocketIO,
    emit
)

from matplotlib.path import Path

from login import (
    database_init,
    user_register,
    user_login,
    get_user_profile
)

from session_manager import (
    login_user,
    logout_user,
    current_user,
    logged_in
)

import json
import eventlet
eventlet.monkey_patch()
import heapq

app = Flask(__name__)

app.secret_key = "saferoute_secret"
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="eventlet"
)

GRID_ROWS = 50
GRID_COLS = 50
GRID_SIZE = 16

with open(
    "saved_floorplans.json",
    "r"
) as f:

    floorplans = json.load(f)

live_zones = {}


# =========================
# A*
# =========================

def heuristic(a, b):

    return (
        abs(a[0] - b[0]) +
        abs(a[1] - b[1])
    )


def polygon_to_cells(points):

    poly = Path(points)

    cells = set()

    for row in range(GRID_ROWS):

        for col in range(GRID_COLS):

            px = (
                col * GRID_SIZE +
                GRID_SIZE / 2
            )

            py = (
                row * GRID_SIZE +
                GRID_SIZE / 2
            )

            if poly.contains_point((px, py)):

                cells.add((col, row))

    return cells

def astar(
    start,
    goal,
    walls,
    danger,
    safe
):

    open_set = []

    heapq.heappush(
        open_set,
        (0, start)
    )

    came_from = {}

    g_score = {
        start: 0
    }

    while open_set:

        current = heapq.heappop(
            open_set
        )[1]

        if current == goal:

            path = []

            while current in came_from:

                path.append(current)

                current = came_from[current]

            path.append(start)

            path.reverse()

            return path

        neighbors = [

            (
                current[0] + 1,
                current[1]
            ),

            (
                current[0] - 1,
                current[1]
            ),

            (
                current[0],
                current[1] + 1
            ),

            (
                current[0],
                current[1] - 1
            )
        ]

        for n in neighbors:

            if (
                n[0] < 0 or
                n[1] < 0 or
                n[0] >= GRID_COLS or
                n[1] >= GRID_ROWS
            ):
                continue

            if n in walls:
                continue

            if n in danger:
                continue

            move_cost = 1

            if n in safe:

                move_cost -= 0.2

            tentative = (
                g_score[current] +
                move_cost
            )

            if (
                n not in g_score or
                tentative < g_score[n]
            ):

                came_from[n] = current

                g_score[n] = tentative

                f = (
                    tentative +
                    heuristic(n, goal)
                )

                heapq.heappush(
                    open_set,
                    (f, n)
                )

    return []


# =========================
# LOGIN
# =========================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login_page():

    if request.method == "GET":

        return render_template(
            "login.html"
        )

    username = request.form["username"]

    password = request.form["password"]

    userid = user_login(
        username,
        password
    )

    if userid is None:

        return render_template(

            "login.html",

            error="Invalid credentials"
        )

    profile = get_user_profile(
        username
    )

    login_user({

        "username": username,

        "role": profile["role"]
    })

    if profile["role"] == "admin":

        return redirect("/teacher")

    return redirect("/")


@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "GET":

        return render_template(
            "register.html"
        )

    username = request.form["username"]

    password = request.form["password"]

    fname = request.form["fname"]

    lname = request.form["lname"]

    role = request.form["role"]

    userid = user_register(

        username,
        password,
        role,
        fname,
        lname
    )

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


# =========================
# STUDENT
# =========================

@app.route("/")
def student():

    if not logged_in():

        return redirect("/login")

    if current_user()["role"] == "admin":

        return redirect("/teacher")

    return render_template(
        "student.html"
    )


# =========================
# TEACHER
# =========================

@app.route("/teacher")
def teacher():

    if not logged_in():

        return redirect("/login")

    if current_user()["role"] != "admin":

        return redirect("/")

    return render_template(
        "teacher.html"
    )




# =========================
# FLOORPLANS
# =========================

@app.route("/floorplans")
def get_floorplans():

    return jsonify(floorplans)


# =========================
# ROUTING
# =========================

@app.route(
    "/route",
    methods=["POST"]
)
def route():

    data = request.json

    building = data["building"]

    start = tuple(
        data["start"]
    )

    fp = next(

        f for f in floorplans

        if f["name"] == building
    )

    walls = set(

        tuple(x)

        for x in fp["walls"]
    )

    exits = [

        tuple(x)

        for x in fp["exits"]
    ]

    danger = set()
    safe = set()

    if building in live_zones:

        for zone in live_zones[building]:

            cells = polygon_to_cells(
                zone["points"]
            )

            if zone["type"] == "danger":

                danger.update(cells)

            if zone["type"] == "safe":

                safe.update(cells)

    best_path = []

    for ex in exits:

        path = astar(

            start,
            ex,
            walls,
            danger,
            safe
        )

        if (
            path and
            (
                not best_path or
                len(path) < len(best_path)
            )
        ):

            best_path = path

    return jsonify(best_path)

@app.route("/zones")
def get_zones():

    return jsonify(live_zones)

# =========================
# LIVE ZONES
# =========================
@socketio.on("zone_update")
def zone_update(data):

    print("ZONE RECEIVED")

    building = data["building"]

    if building not in live_zones:

        live_zones[building] = []

    live_zones[building].append(data)

    socketio.emit(
        "zone_sync",
        data
    )

# =========================
# RUN
# =========================

if __name__ == "__main__":

    socketio.run(
        app,
        debug=True,
        port =5050
    )