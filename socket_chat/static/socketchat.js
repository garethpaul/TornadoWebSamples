(function() {

  jQuery(function($) {
    var error, log, messages, websocket;
    log = function(message) {
      return typeof console !== "undefined" && console !== null ? console.log(message) : void 0;
    };
    error = function(message) {
      return typeof console !== "undefined" && console !== null ? console.error(message) : void 0;
    };
    messages = $('ul#messages');
    websocket = new WebSocket('ws://localhost:8000/message');
    websocket.onmessage = function(event) {
      log("Receive: " + event.data);
      return messages.append($("<li>").text(event.data));
    };
    websocket.onerror = function(event) {
      return error(event);
    };
    return $('input#message').keypress(function(e) {
      var data;
      if (e.keyCode === 13) {
        e.preventDefault();
        log("Sending Message: " + this.value);
        data = {
          action: 'add',
          body: this.value
        };
        websocket.send(JSON.stringify(data));
        return this.value = '';
      }
    });
  });

}).call(this);
