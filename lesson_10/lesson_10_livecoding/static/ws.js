const ws = new WebSocket("ws://" + location.host + '/ws');

ws.onmessage = event => {
    const li = document.createElement('li');
    li.innerText = event.data;
    document.getElementById("messages").appendChild(li);
}

function sendMessage() {
    const input = document.getElementById("msgInput");
    ws.send(input.value);
    input.value = ""
}