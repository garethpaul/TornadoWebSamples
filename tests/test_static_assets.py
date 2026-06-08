from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_asset(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_comet_chat_renders_messages_as_text_nodes():
    coffee = read_asset("comet_chat/static/cometchat.coffee")
    javascript = read_asset("comet_chat/static/cometchat.js")

    assert 'messages.append "<li>' not in coffee
    assert 'li = "<li>' not in coffee
    assert 'messages.append("<li>"' not in javascript
    assert 'li = "<li>"' not in javascript
    assert 'messages.append $("<li>").text data.message' in coffee
    assert 'messages.append($("<li>").text(data.message))' in javascript


def test_socket_chat_renders_messages_as_text_nodes():
    coffee = read_asset("socket_chat/static/socketchat.coffee")
    javascript = read_asset("socket_chat/static/socketchat.js")

    assert 'messages.append "<li>' not in coffee
    assert 'li = "<li>' not in coffee
    assert 'messages.append("<li>"' not in javascript
    assert 'li = "<li>"' not in javascript
    assert "#{message}" not in coffee
    assert "+ message +" not in javascript
    assert 'messages.append $("<li>").text event.data' in coffee
    assert 'messages.append($("<li>").text(event.data))' in javascript


def test_socket_chat_reports_browser_errors_to_console():
    coffee = read_asset("socket_chat/static/socketchat.coffee")
    javascript = read_asset("socket_chat/static/socketchat.js")

    assert "console?.error message" in coffee
    assert "console.error(message)" in javascript
    assert "console?.erro message" not in coffee
    assert "console.erro(message)" not in javascript
