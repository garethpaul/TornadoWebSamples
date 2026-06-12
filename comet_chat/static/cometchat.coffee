form = document.querySelector '#message-form'
input = document.querySelector '#message'
messages = document.querySelector '#messages'

appendMessage = (message) ->
    item = document.createElement 'li'
    item.textContent = message
    messages.appendChild item

poll = ->
    fetch('/message',
        credentials: 'same-origin'
        headers:
            Accept: 'application/json'
    ).then((response) ->
        throw new Error "Message poll failed: #{response.status}" unless response.ok
        response.json()
    ).then((data) ->
        appendMessage data.message
        setTimeout poll, 0
    ).catch((error) ->
        console.error error
        setTimeout poll, 1000
    )

form.addEventListener 'submit', (event) ->
    event.preventDefault()
    fetch('/message',
        method: 'POST'
        body: new FormData(form)
        credentials: 'same-origin'
        headers:
            Accept: 'application/json'
    ).then((response) ->
        throw new Error "Message send failed: #{response.status}" unless response.ok
        input.value = ''
    ).catch (error) ->
        console.error error

setTimeout poll, 200
