const chats = {};
let selectedUser = null;

const protocol =
    location.protocol === "https:" ? "wss://" : "ws://";

const socket = new WebSocket(protocol + location.host + "/ws");

// ── C3 FIX: Real AES-GCM encryption via WebCrypto API ──

async function deriveKey(user1, user2) {
    const enc = new TextEncoder();
    const pair = [user1, user2].sort().join("-");

    const keyMaterial = await crypto.subtle.importKey(
        "raw",
        enc.encode(pair),
        "PBKDF2",
        false,
        ["deriveKey"]
    );

    return crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: enc.encode("shadow-chat-v2-salt"),
            iterations: 100000,
            hash: "SHA-256",
        },
        keyMaterial,
        { name: "AES-GCM", length: 256 },
        false,
        ["encrypt", "decrypt"]
    );
}

async function encryptMessage(text, user1, user2) {
    const key = await deriveKey(user1, user2);
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const enc = new TextEncoder();

    const encrypted = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv: iv },
        key,
        enc.encode(text)
    );

    return {
        data: btoa(String.fromCharCode(...new Uint8Array(encrypted))),
        iv: btoa(String.fromCharCode(...iv)),
    };
}

async function decryptMessage(encryptedData, ivBase64, user1, user2) {
    try {
        const key = await deriveKey(user1, user2);
        const iv = Uint8Array.from(atob(ivBase64), (c) =>
            c.charCodeAt(0)
        );
        const data = Uint8Array.from(atob(encryptedData), (c) =>
            c.charCodeAt(0)
        );

        const decrypted = await crypto.subtle.decrypt(
            { name: "AES-GCM", iv: iv },
            key,
            data
        );

        return new TextDecoder().decode(decrypted);
    } catch {
        return "[decryption failed]";
    }
}

function room(a, b) {
    return [a, b].sort().join("-");
}

socket.onmessage = function (event) {
    const data = JSON.parse(event.data);

    if (data.type === "users") {
        renderUsers(data.users);
        return;
    }

    if (data.type === "history") {
        Object.assign(chats, data.chats);
        renderChat();
        return;
    }

    saveMessage(data);
};

function saveMessage(data) {
    const r = room(data.sender, data.receiver);

    if (!chats[r]) chats[r] = [];

    chats[r].push(data);
    renderChat();
}

// C5 FIX: Safe DOM construction for user list
function renderUsers(users) {
    const userList = document.getElementById("userList");
    userList.innerHTML = "";

    users.forEach(function (user) {
        if (user === CURRENT_USER) return;

        // Build DOM safely — no innerHTML with user data
        const div = document.createElement("div");
        div.className = "user";
        div.id = user;
        div.textContent = user;
        div.addEventListener("click", function () {
            selectUser(user);
        });

        userList.appendChild(div);
    });
}

function selectUser(user) {
    selectedUser = user;

    document
        .querySelectorAll(".user")
        .forEach(function (u) {
            u.classList.remove("active");
        });

    var el = document.getElementById(user);
    if (el) el.classList.add("active");

    document.getElementById("title").innerText = user;
    renderChat();
}

// C4 FIX: Safe DOM construction for chat messages
async function renderChat() {
    const chat = document.getElementById("chat");
    chat.innerHTML = "";

    if (!selectedUser) return;

    const r = room(CURRENT_USER, selectedUser);

    if (!chats[r]) return;

    for (const msg of chats[r]) {
        let text = "";

        if (msg.iv) {
            // AES-GCM message (v2)
            if (msg.receiver === CURRENT_USER) {
                text = await decryptMessage(
                    msg.encrypted,
                    msg.iv,
                    CURRENT_USER,
                    msg.sender
                );
            } else {
                text = await decryptMessage(
                    msg.encrypted,
                    msg.iv,
                    CURRENT_USER,
                    selectedUser
                );
            }
        } else {
            // Legacy XOR fallback (v1 messages)
            text = legacyDecrypt(
                msg.encrypted,
                msg.receiver === CURRENT_USER
                    ? CURRENT_USER
                    : selectedUser
            );
        }

        const type =
            msg.sender === CURRENT_USER ? "sent" : "received";

        // Build DOM safely — no innerHTML with message text
        const div = document.createElement("div");
        div.className = "message " + type;
        div.textContent = text;
        chat.appendChild(div);
    }

    chat.scrollTop = chat.scrollHeight;
}

// Legacy decrypt for old messages during migration
function legacyDecrypt(text, name) {
    let total = 0;
    for (let i = 0; i < name.length; i++) {
        total += name.charCodeAt(i);
    }
    const key = (total % 20) + 1;
    const decoded = atob(text);
    let result = "";
    for (let i = 0; i < decoded.length; i++) {
        result += String.fromCharCode(
            decoded.charCodeAt(i) ^ key
        );
    }
    return result;
}

async function sendMessage() {
    if (!selectedUser) return;

    const input = document.getElementById("message");
    const message = input.value.trim();

    if (message === "") return;

    // C3 FIX: Use real AES-GCM encryption
    const { data, iv } = await encryptMessage(
        message,
        CURRENT_USER,
        selectedUser
    );

    const msgData = {
        type: "message",
        sender: CURRENT_USER,
        receiver: selectedUser,
        encrypted: data,
        iv: iv,
    };

    socket.send(JSON.stringify(msgData));
    saveMessage(msgData);

    input.value = "";
}

document
    .getElementById("message")
    .addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

document
    .getElementById("mobileUserSelect")
    .addEventListener("change", function () {
        if (this.value) {
            selectUser(this.value);
        }
    });

function toggleUsers() {
    document
        .querySelector(".users")
        .classList.toggle("show-users");
}
