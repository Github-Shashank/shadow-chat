# Shadow Chat

A modular real-time encrypted chat application built using Python, Flask, and WebSockets.

## Features

- Real-time messaging
- User authentication
- Password hashing using bcrypt
- Encrypted message transfer
- Persistent message storage
- Online user system
- Mobile responsive UI
- WebSocket communication
- Cloud deployment support

## Tech Stack

- Python
- Flask
- Flask-Sock
- WebSockets
- HTML/CSS/JavaScript
- bcrypt

## Installation

Clone repository:

```bash
git clone https://github.com/YOUR_USERNAME/shadow-chat.git
cd shadow-chat
````

Create virtual environment:

```bash
python -m venv venv
```

Activate virtual environment:

### Windows

```bash
venv\Scripts\activate
```

### Linux/Mac

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run application:

```bash
python app.py
```

Open browser:

```text
http://127.0.0.1:5000
```

## Deployment

This project is deployable on platforms like:

* Render
* Railway

## Project Structure

```text
encrypted_chat/
│
├── app.py
├── requirements.txt
├── Procfile
├── users.json
├── messages.json
│
├── routes/
├── websocket/
├── templates/
└── static/
```

## Screenshots

Add screenshots here.

## Future Improvements

* End-to-end encryption
* Group chats
* File sharing
* Voice messages
* Database integration
* Push notifications
* Read receipts
* Message search

## License

MIT License