const chats = {};

let selectedUser = null;

const socket =
    new WebSocket(
        "ws://" + location.host + "/ws"
    );

function getKey(name){

    let total = 0;

    for(let i=0;i<name.length;i++){

        total += name.charCodeAt(i);
    }

    return total % 20 + 1;
}

function encrypt(text, key){

    let result = "";

    for(let i=0;i<text.length;i++){

        result += String.fromCharCode(
            text.charCodeAt(i) ^ key
        );
    }

    return btoa(result);
}

function decrypt(text, key){

    let decoded = atob(text);

    let result = "";

    for(let i=0;i<decoded.length;i++){

        result += String.fromCharCode(
            decoded.charCodeAt(i) ^ key
        );
    }

    return result;
}

function room(a,b){

    return [a,b].sort().join("-");
}

socket.onmessage = function(event){

    const data =
        JSON.parse(event.data);

    // ONLINE USERS

    if(data.type === "users"){

        renderUsers(data.users);
        return;
    }

    // LOAD OLD CHAT HISTORY

    if(data.type === "history"){

        Object.assign(
            chats,
            data.chats
        );

        renderChat();

        return;
    }

    // NORMAL MESSAGE

    saveMessage(data);
};

function saveMessage(data){

    const r =
        room(
            data.sender,
            data.receiver
        );

    if(!chats[r])
        chats[r] = [];

    chats[r].push(data);

    renderChat();
}

function sendMessage(){

    if(!selectedUser)
        return;

    const input =
        document.getElementById("message");

    const message =
        input.value.trim();

    if(message === "")
        return;

    const encrypted =
        encrypt(
            message,
            getKey(selectedUser)
        );

    const data = {

        type: "message",

        sender: CURRENT_USER,

        receiver: selectedUser,

        encrypted: encrypted
    };

    socket.send(
        JSON.stringify(data)
    );

    saveMessage(data);

    input.value = "";
}

function renderUsers(users){

    const userList =
        document.getElementById(
            "userList"
        );

    userList.innerHTML = "";

    users.forEach(user => {

        if(user === CURRENT_USER)
            return;

        userList.innerHTML += `

            <div
                class="user"
                onclick="selectUser('${user}')"
                id="${user}"
            >

                ${user}

            </div>
        `;
    });
}

function selectUser(user){

    selectedUser = user;

    document.querySelectorAll(".user")
        .forEach(u => u.classList.remove("active"));

    document.getElementById(user)
        .classList.add("active");

    document.getElementById("title")
        .innerText = user;

    renderChat();
}

function renderChat(){

    const chat =
        document.getElementById("chat");

    chat.innerHTML = "";

    if(!selectedUser)
        return;

    const r =
        room(
            CURRENT_USER,
            selectedUser
        );

    if(!chats[r])
        return;

    chats[r].forEach(msg => {

        let text = "";

        if(msg.receiver === CURRENT_USER){

            text = decrypt(
                msg.encrypted,
                getKey(CURRENT_USER)
            );

        }else{

            text = decrypt(
                msg.encrypted,
                getKey(selectedUser)
            );
        }

        const type =
            msg.sender === CURRENT_USER
            ? "sent"
            : "received";

        chat.innerHTML += `

        <div class="message ${type}">

            ${text}

        </div>
        `;

    });

    chat.scrollTop =
        chat.scrollHeight;
}

document
.getElementById("message")
.addEventListener(
    "keypress",
    function(event){

        if(event.key === "Enter"){

            sendMessage();
        }
    }
);

document
.getElementById("mobileUserSelect")
.addEventListener(
    "change",
    function(){

        if(this.value){

            selectUser(this.value);
        }
    }
);

function toggleUsers(){

    document
    .querySelector(".users")
    .classList.toggle("show-users");
}