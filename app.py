from flask import Flask
from flask_sock import Sock

from routes.auth import auth_bp
from routes.chat import chat_bp
from websocket.socket_handler import register_socket

app = Flask(__name__)

app.secret_key = "secret123"

sock = Sock(app)

# Register routes
app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)

# Register websocket
register_socket(sock)

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )