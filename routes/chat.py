import time
from flask import Blueprint, session, redirect, render_template

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/")
def home():
    # L3 FIX: Validate session hasn't expired
    if "user" not in session:
        return redirect("/login")

    login_time = session.get("login_time", 0)
    if time.time() - login_time > 1800:  # 30 minutes
        session.clear()
        return redirect("/login")

    return render_template("chat.html", username=session["user"])
