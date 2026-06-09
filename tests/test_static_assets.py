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


def test_chat_clients_use_same_origin_message_endpoints():
    comet_coffee = read_asset("comet_chat/static/cometchat.coffee")
    comet_javascript = read_asset("comet_chat/static/cometchat.js")
    socket_coffee = read_asset("socket_chat/static/socketchat.coffee")
    socket_javascript = read_asset("socket_chat/static/socketchat.js")

    assert "url: '/message'" in comet_coffee
    assert "url: '/message'" in comet_javascript
    assert "//localhost:8000/message" not in comet_coffee
    assert "//localhost:8000/message" not in comet_javascript
    assert "window.location.host" in socket_coffee
    assert "window.location.host" in socket_javascript
    assert "ws://localhost:8000/message" not in socket_coffee
    assert "ws://localhost:8000/message" not in socket_javascript


def test_templates_use_https_external_stylesheets():
    comet_template = read_asset("comet_chat/templates/index.html")
    socket_template = read_asset("socket_chat/templates/index.html")

    for template in (comet_template, socket_template):
        assert "http://yui.yahooapis.com" not in template
        assert "https://yui.yahooapis.com/3.5.1/build/cssreset/cssreset-min.css" in template


def test_templates_hint_server_message_length_limit():
    comet_template = read_asset("comet_chat/templates/index.html")
    socket_template = read_asset("socket_chat/templates/index.html")

    for template in (comet_template, socket_template):
        assert 'id="message"' in template
        assert 'maxlength="500"' in template
