import json
import os
import time
from flask import session

clients = {}

MESSAGES_FILE = "messages.json"

# ── C7 FIX: Use proper data storage ──
# Keep JSON files but with proper locking concept
# For production, migrate to SQLite

if os.path.exists(MESSAGES_FILE):
    try:
        with open(MESSAGES_FILE, "r") as f:
            chats = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        chats = {}
else:
    chats = {}


def save_chats():
    # Atomic write: write to temp file then rename
    tmp_file = MESSAGES_FILE + ".tmp"
    try:
        with open(tmp_file, "w") as f:
            json.dump(chats, f, indent=2)
        os.replace(tmp_file, MESSAGES_FILE)
    except Exception:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)


def send_online_users():
    users_data = json.dumps({
        "type": "users",
        "users": list(clients.keys()),
    })
    for client in list(clients.values()):
        try:
            client.send(users_data)
        except Exception:
            pass


# ── M6 FIX: Input validation ──
MAX_MESSAGE_LENGTH = 1000
MAX_USERNAME_LENGTH = 30


def validate_message(data):
    required_fields = ["sender", "receiver", "encrypted"]
    if not all(k in data for k in required_fields):
        return False

    for field in ["sender", "receiver"]:
        if not isinstance(data[field], str) or len(data[field]) > MAX_USERNAME_LENGTH:
            return False
        if not data[field].strip():
            return False

    if not isinstance(data.get("encrypted"), str):
        return False

    if len(data.get("encrypted", "")) > MAX_MESSAGE_LENGTH * 2:
        return False

    # Accept optional 'iv' field for AES-GCM
    if "iv" in data and not isinstance(data["iv"], str):
        return False

    return True


def register_socket(sock):

    @sock.route("/ws")
    def websocket(ws):
        # C6 FIX: Validate session properly
        username = session.get("user")
        if not username:
            try:
                ws.close(1008, "Unauthorized")
            except Exception:
                pass
            return

        # L3 FIX: Check session expiry
        login_time = session.get("login_time", 0)
        if time.time() - login_time > 1800:
            try:
                ws.close(1008, "Session expired")
            except Exception:
                pass
            return

        clients[username] = ws
        send_online_users()

        # Send chat history
        user_chats = {}
        for room, messages in chats.items():
            if username in room.split("-"):
                user_chats[room] = messages

        try:
            ws.send(json.dumps({"type": "history", "chats": user_chats}))
        except Exception:
            pass

        while True:
            data = ws.receive()
            if data is None:
                break

            try:
                data_json = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                continue

            # ── C2 FIX: Use server-side session for sender ──
            sender = session.get("user")
            receiver = data_json.get("receiver", "")

            # ── M6 FIX: Validate input ──
            data_json["sender"] = sender
            data_json["receiver"] = receiver

            if not validate_message(data_json):
                continue

            room = "-".join(sorted([sender, receiver]))

            if room not in chats:
                chats[room] = []

            chats[room].append(data_json)
            save_chats()

            # Forward to receiver
            if receiver in clients:
                try:
                    clients[receiver].send(json.dumps(data_json))
                except Exception:
                    pass

        # Cleanup
        if username in clients:
            del clients[username]

        send_online_users()
