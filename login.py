# =========================
# login.py
# =========================

import sqlite3
import uuid

DATABASE_NAME = "users.db"


# =========================
# DATABASE INIT
# =========================

def database_init():

    with sqlite3.connect(DATABASE_NAME) as db:

        db.execute("""

        CREATE TABLE IF NOT EXISTS users(

            id TEXT PRIMARY KEY,

            username TEXT UNIQUE,

            password TEXT,

            role TEXT,

            fname TEXT,

            lname TEXT
        )

        """)

        db.commit()


# =========================
# REGISTER
# =========================

def user_register(

    username,
    password,
    role,
    fname,
    lname
):

    with sqlite3.connect(DATABASE_NAME) as db:

        cursor = db.execute(

            "SELECT * FROM users WHERE username=?",

            (username,)
        )

        if cursor.fetchone():

            return -1

        userid = str(uuid.uuid4())

        db.execute(

            """

            INSERT INTO users(

                id,
                username,
                password,
                role,
                fname,
                lname

            )

            VALUES(?,?,?,?,?,?)

            """,

            (
                userid,
                username,
                password,
                role,
                fname,
                lname
            )
        )

        db.commit()

        return userid


# =========================
# LOGIN
# =========================

def user_login(

    username,
    password
):

    with sqlite3.connect(DATABASE_NAME) as db:

        cursor = db.execute(

            """

            SELECT id

            FROM users

            WHERE username=?
            AND password=?

            """,

            (
                username,
                password
            )
        )

        result = cursor.fetchone()

        if result:

            return result[0]

        return None


# =========================
# PROFILE
# =========================

def get_user_profile(username):

    with sqlite3.connect(DATABASE_NAME) as db:

        cursor = db.execute(

            """

            SELECT

                username,
                role,
                fname,
                lname

            FROM users

            WHERE username=?

            """,

            (username,)
        )

        result = cursor.fetchone()

        if not result:

            return None

        return {

            "username": result[0],

            "role": result[1],

            "fname": result[2],

            "lname": result[3]
        }