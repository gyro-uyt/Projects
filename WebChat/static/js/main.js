let userId = null;
const ws = new WebSocket(`ws://${window.location.host}/ws`);

ws.onmessage = function (event) {
  const messages = document.getElementById("messages");
  const data = JSON.parse(event.data);

  if (data.type === "welcome") {
    userId = data.user_id;
    return;
  }

  const message = document.createElement("div");
  message.className = "my-2 p-2 rounded-lg";

  if (data.type === "system") {
    message.className += " text-center text-gray-500";
    message.textContent = data.message;
  } else if (data.type === "chat") {
    if (data.sender_id === userId) {
      message.className += " message-sent";
    } else {
      message.className += " message-received";
    }

    if (data.is_admin) {
      message.className += " admin-message";
    }

    message.textContent = `${data.author}: ${data.message}`;
  }

  messages.appendChild(message);
  messages.scrollTop = messages.scrollHeight;
};

function sendMessage(event) {
  const input = document.getElementById("messageText");
  if (input.value) {
    ws.send(input.value);
    input.value = "";
  }
  event.preventDefault();
}

document.getElementById("form").addEventListener("submit", sendMessage);
