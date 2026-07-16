(function() {
  "use strict";

  var form = document.querySelector("#message-form");
  var input = document.querySelector("#message");
  var messages = document.querySelector("#messages");

  function appendMessage(message) {
    var item = document.createElement("li");
    item.textContent = message;
    messages.appendChild(item);
  }

  function poll() {
    fetch("/message", {
      credentials: "same-origin",
      headers: {Accept: "application/json"}
    })
      .then(function(response) {
        if (!response.ok) {
          throw new Error("Message poll failed: " + response.status);
        }
        if (response.status === 204) {
          return null;
        }
        return response.json();
      })
      .then(function(data) {
        if (data !== null) {
          appendMessage(data.message);
        }
        setTimeout(poll, 0);
      })
      .catch(function(error) {
        console.error(error);
        setTimeout(poll, 1000);
      });
  }

  form.addEventListener("submit", function(event) {
    event.preventDefault();
    fetch("/message", {
      method: "POST",
      body: new FormData(form),
      credentials: "same-origin",
      headers: {Accept: "application/json"}
    })
      .then(function(response) {
        if (!response.ok) {
          throw new Error("Message send failed: " + response.status);
        }
        input.value = "";
      })
      .catch(function(error) {
        console.error(error);
      });
  });

  setTimeout(poll, 200);
}());
