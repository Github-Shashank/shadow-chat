import os
import secrets
import time
from flask import Flask, request, g
from flask_sock import Sock
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from routes.auth import auth_bp
from routes.chat import chat_bp
from websocket.socket_handler import register_socket

app = Flask(__name__)

# ── C1 FIX: No hardcoded fallback — fail if SECRET_KEY not set ──
app.secret_key = os.environ["SECRET_KEY"]

# ── M3 FIX: Secure session cookies ──
app.config.update(
    SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "true").lower() == "true",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=1800,  # 30 minutes (L3)
)

# ── H1 FIX: CSRF protection ──
csrf = CSRFProtect(app)

# ── H5 FIX: Rate limiting ──
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per minute"],
    storage_uri="memory://",
)

sock = Sock(app)

# Register routes
app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)

# Register websocket
register_socket(sock)


# ── M7 FIX: Security headers ──
@app.after_request
def set_security_headers(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    return response


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",  # M1 FIX: localhost only
        port=int(os.environ.get("PORT", 5000)),
    )
