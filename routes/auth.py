from flask import Blueprint
from flask import request
from flask import redirect
from flask import session
from flask import render_template

import json

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

        if username in users and users[username] == password:

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

        users[username] = password

        with open("users.json", "w") as f:
            json.dump(users, f)

        return redirect("/login")

    return render_template("signup.html")

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/login")