# Shadow Chat

A modular real-time encrypted chat application built using Python, Flask, and WebSockets with **end-to-end AES-256-GCM encryption**.

## Features

- Real-time messaging via WebSockets
- User authentication with bcrypt password hashing
- **End-to-end AES-256-GCM encryption** (WebCrypto API)
- CSRF protection on all forms
- Rate limiting on authentication endpoints
- Secure session management with expiry
- Security headers (CSP, HSTS, X-Frame-Options)
- Persistent message storage
- Online user system
- Mobile responsive UI

## Security Features

| Feature | Implementation |
|---------|---------------|
| **Encryption** | AES-256-GCM via WebCrypto API with PBKDF2 key derivation |
| **CSRF** | Flask-WTF CSRFProtect on all forms |
| **Rate Limiting** | Flask-Limiter on auth endpoints |
| **Session Security** | HttpOnly, Secure, SameSite cookies with 30-min timeout |
| **Password Policy** | Min 8 chars, uppercase, lowercase, digit required |
| **Security Headers** | CSP, X-Frame-Options, HSTS, X-Content-Type-Options |
| **XSS Prevention** | Safe DOM construction (no innerHTML with user data) |
| **Auth Spoofing** | Server-side session identity (never trusts client sender) |

## Tech Stack

- Python / Flask
- Flask-Sock (WebSockets)
- Flask-WTF (CSRF Protection)
- Flask-Limiter (Rate Limiting)
- bcrypt (Password Hashing)
- WebCrypto API (AES-256-GCM Encryption)
- HTML / CSS / JavaScript

## Installation

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/shadow-chat.git
cd shadow-chat
python -m venv venv
source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set a secure `SECRET_KEY`:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Run

```bash
# Development
python app.py

# Production
gunicorn app:app
```

> **Note:** `SECRET_KEY` environment variable is **required**. The app will not start without it.

## Project Structure

```
shadow-chat/
├── app.py                  # Flask app entry point
├── routes/
│   ├── auth.py             # Login / Signup / Logout
│   └── chat.py             # Chat page route
├── websocket/
│   └── socket_handler.py   # WebSocket message handling
├── static/
│   ├── script.js           # Client-side JS (WebCrypto encryption)
│   ├── style.css           # Styles
├── templates/
│   ├── chat.html           # Chat page
│   ├── login.html          # Login page
│   └── signup.html         # Signup page
├── requirements.txt        # Python dependencies
├── Procfile                # Deployment config
├── .env.example            # Environment template
└── README.md
```

## License

MIT
