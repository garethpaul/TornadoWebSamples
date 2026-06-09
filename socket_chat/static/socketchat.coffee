jQuery ($) ->

    # simple log
    log = (message) -> console?.log message
    error = (message) -> console?.error message

    messages = $ 'ul#messages'

    messagePath = '/message'
    websocketScheme = if window.location.protocol is 'https:' then 'wss://' else 'ws://'
    websocket = new WebSocket "#{websocketScheme}#{window.location.host}#{messagePath}"

    websocket.onmessage = (event) ->
        log "Receive: #{event.data}"
        messages.append $("<li>").text event.data

    websocket.onerror = (event) ->
        error event

    $('input#message').keypress (e) ->
        if e.keyCode is 13
            e.preventDefault()
            log "Sending Message: #{@value}"
            data =
                action: 'add'
                body: @value
            websocket.send JSON.stringify data
            @value = ''
