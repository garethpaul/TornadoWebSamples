form = document.querySelector '#message-form'
input = document.querySelector '#message'
messages = document.querySelector '#messages'
websocketScheme = if window.location.protocol is 'https:' then 'wss://' else 'ws://'
websocket = new WebSocket websocketScheme + window.location.host + '/message'

appendMessage = (message) ->
    item = document.createElement 'li'
    item.textContent = message
    messages.appendChild item

websocket.addEventListener 'message', (event) ->
    appendMessage event.data

websocket.addEventListener 'error', (event) ->
    console.error event

form.addEventListener 'submit', (event) ->
    event.preventDefault()
    unless websocket.readyState is WebSocket.OPEN
        console.error 'WebSocket is not ready'
        return
    websocket.send JSON.stringify action: 'add', body: input.value
    input.value = ''
