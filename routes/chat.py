from flask import Blueprint
from flask import session
from flask import redirect
from flask import render_template

chat_bp = Blueprint(
    "chat",
    __name__
)

@chat_bp.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "chat.html",
        username=session["user"]
    )