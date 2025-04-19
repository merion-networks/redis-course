const ws = new WebSocket("ws://" + location.host + "/ws");
    ws.onmessage = function(event) {
      const box = document.getElementById("chat-box");
      const message = document.createElement("div");
      message.innerHTML = `<b>New:</b> ${event.data}`;
      box.appendChild(message);
      box.scrollTop = box.scrollHeight;
    };