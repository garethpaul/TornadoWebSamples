from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_asset(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_chat_clients_render_messages_as_text_nodes():
    for relative_path in (
        "comet_chat/static/cometchat.coffee",
        "comet_chat/static/cometchat.js",
        "socket_chat/static/socketchat.coffee",
        "socket_chat/static/socketchat.js",
    ):
        client = read_asset(relative_path)
        assert "document.createElement" in client
        assert ".textContent" in client
        assert ".innerHTML" not in client


def test_chat_clients_use_native_browser_apis():
    comet = read_asset("comet_chat/static/cometchat.js")
    socket = read_asset("socket_chat/static/socketchat.js")

    assert 'fetch("/message"' in comet
    assert "new FormData(form)" in comet
    assert 'credentials: "same-origin"' in comet
    assert "new WebSocket(" in socket
    assert "window.location.host" in socket
    assert "WebSocket.OPEN" in socket

    for client in (comet, socket):
        assert "jQuery" not in client
        assert "$.ajax" not in client

    for relative_path in (
        "comet_chat/static/cometchat.coffee",
        "socket_chat/static/socketchat.coffee",
    ):
        client = read_asset(relative_path)
        assert "jQuery" not in client
        assert "$.ajax" not in client


def test_chat_clients_report_browser_errors_to_console():
    comet = read_asset("comet_chat/static/cometchat.js")
    socket = read_asset("socket_chat/static/socketchat.js")

    assert "console.error(error)" in comet
    assert "console.error(event)" in socket
    assert 'console.error("WebSocket is not ready")' in socket


def test_comet_client_treats_no_content_as_normal_repoll():
    coffee = read_asset("comet_chat/static/cometchat.coffee")
    javascript = read_asset("comet_chat/static/cometchat.js")

    assert "response.status is 204" in coffee
    assert "appendMessage data.message unless data is null" in coffee
    assert "response.status === 204" in javascript
    assert "if (data !== null)" in javascript


def test_templates_are_self_contained_and_submit_to_same_origin():
    for sample in ("comet_chat", "socket_chat"):
        template = read_asset(f"{sample}/templates/index.html")
        assert "http://" not in template
        assert "https://" not in template
        assert "jquery" not in template.lower()
        assert "yui" not in template.lower()
        assert 'action="/message"' in template
        assert 'id="message-form"' in template
        assert 'name="message"' in template


def test_comet_template_includes_tornado_xsrf_token():
    template = read_asset("comet_chat/templates/index.html")

    assert "{% module xsrf_form_html() %}" in template


def test_templates_hint_server_message_length_limit():
    for sample in ("comet_chat", "socket_chat"):
        template = read_asset(f"{sample}/templates/index.html")
        assert 'id="message"' in template
        assert 'maxlength="500"' in template


def test_local_styles_replace_external_reset_stylesheet():
    for sample, stylesheet in (
        ("comet_chat", "cometchat.css"),
        ("socket_chat", "socketchat.css"),
    ):
        css = read_asset(f"{sample}/static/{stylesheet}")
        assert "box-sizing: border-box" in css
        assert "list-style: none" in css
        assert "margin: 0" in css
        assert "padding: 0" in css
