# =========================
# session_manager.py
# =========================

from flask import session


def login_user(user):

    session["user"] = user


def logout_user():

    session.pop("user", None)


def current_user():

    return session.get("user")


def logged_in():

    return "user" in session