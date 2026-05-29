from flask import session
import json
import os

clients = {}

MESSAGES_FILE = "messages.json"

# ---------------- LOAD MESSAGES ---------------- #

if os.path.exists(MESSAGES_FILE):

    with open(MESSAGES_FILE, "r") as f:

        try:
            chats = json.load(f)
        except:
            chats = {}

else:

    chats = {}

# ---------------- SAVE ---------------- #

def save_chats():

    with open(MESSAGES_FILE, "w") as f:

        json.dump(chats, f)

# ---------------- SEND ONLINE USERS ---------------- #

def send_online_users():

    users_data = json.dumps({

        "type": "users",

        "users": list(clients.keys())
    })

    for client in clients.values():

        try:
            client.send(users_data)
        except:
            pass

# ---------------- REGISTER SOCKET ---------------- #

def register_socket(sock):

    @sock.route("/ws")
    def websocket(ws):

        username = session.get("user")

        if not username:
            return

        clients[username] = ws

        send_online_users()

        # SEND OLD CHATS

        ws.send(json.dumps({

            "type": "history",

            "chats": chats
        }))

        while True:

            data = ws.receive()

            if data is None:
                break

            data_json = json.loads(data)

            sender = data_json["sender"]
            receiver = data_json["receiver"]

            room = "-".join(
                sorted([sender, receiver])
            )

            # STORE MESSAGE

            if room not in chats:
                chats[room] = []

            chats[room].append(data_json)

            save_chats()

            # SEND TO RECEIVER

            if receiver in clients:

                try:
                    clients[receiver].send(data)
                except:
                    pass

        if username in clients:
            del clients[username]

        send_online_users()