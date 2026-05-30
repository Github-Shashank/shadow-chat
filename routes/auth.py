from flask import Blueprint
from flask import request
from flask import redirect
from flask import session
from flask import render_template

import json
import bcrypt

auth_bp = Blueprint(
    "auth",
    __name__
)

# Load users
try:

    with open("users.json", "r") as f:
        users = json.load(f)

except:

    users = {}

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username in users and bcrypt.checkpw(
            password.encode(),
            users[username].encode()
        ):

            session["user"] = username

            return redirect("/")

        return "Invalid Login"

    return render_template("login.html")

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            return "User already exists"

        hashed_password = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

        users[username] = hashed_password

        with open("users.json", "w") as f:
            json.dump(users, f)

        return redirect("/login")

    return render_template("signup.html")

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/login")