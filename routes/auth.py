import json
import os
import re
import time
import bcrypt
from flask import Blueprint, request, redirect, session, render_template, url_for, current_app

auth_bp = Blueprint("auth", __name__)

USERS_FILE = "users.json"


# ── L1 FIX: Specific exception handling ──
def _load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def _save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


# ── H4 FIX: Password complexity validation ──
def _validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain an uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain a lowercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain a digit"
    return True, ""


def _validate_username(username):
    if len(username) < 3 or len(username) > 30:
        return False, "Username must be 3-30 characters"
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username may only contain letters, numbers, and underscores"
    return True, ""


@auth_bp.route("/login", methods=["GET", "POST"])
# H5 FIX: Rate limit on login
def login():
    from app import limiter

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        users = _load_users()

        # H6 FIX: Generic error — no user enumeration
        if (
            not username
            or not password
            or username not in users
            or not bcrypt.checkpw(password.encode(), users[username].encode())
        ):
            return render_template("login.html", error="Invalid username or password"), 401

        # ── L3 FIX: Track session time ──
        session.permanent = True
        session["user"] = username
        session["login_time"] = time.time()

        return redirect("/")

    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # H4 FIX: Validate password
        valid, msg = _validate_password(password)
        if not valid:
            return render_template("signup.html", error=msg), 400

        # Validate username
        valid, msg = _validate_username(username)
        if not valid:
            return render_template("signup.html", error=msg), 400

        users = _load_users()

        # H6 FIX: Generic error — no user enumeration
        if username in users:
            return render_template("signup.html", error="Username already taken"), 409

        hashed_password = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()
        ).decode()

        users[username] = hashed_password
        _save_users(users)

        return redirect("/login")

    return render_template("signup.html")


@auth_bp.route("/logout", methods=["POST"])
# H2 FIX: POST-only logout
def logout():
    session.clear()
    return redirect("/login")
