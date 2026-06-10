(function() {
  "use strict";

  var form = document.querySelector("#message-form");
  var input = document.querySelector("#message");
  var messages = document.querySelector("#messages");
  var websocketScheme = window.location.protocol === "https:" ? "wss://" : "ws://";
  var websocket = new WebSocket(websocketScheme + window.location.host + "/message");

  function appendMessage(message) {
    var item = document.createElement("li");
    item.textContent = message;
    messages.appendChild(item);
  }

  websocket.addEventListener("message", function(event) {
    appendMessage(event.data);
  });

  websocket.addEventListener("error", function(event) {
    console.error(event);
  });

  form.addEventListener("submit", function(event) {
    event.preventDefault();
    if (websocket.readyState !== WebSocket.OPEN) {
      console.error("WebSocket is not ready");
      return;
    }
    websocket.send(JSON.stringify({action: "add", body: input.value}));
    input.value = "";
  });
}());
