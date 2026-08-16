from __future__ import annotations

import json
import threading
from http.client import HTTPConnection
from urllib.request import Request, urlopen

import pytest

from cleaner.app import CleanmarkHTTPServer, Handler, MAX_FILE_BYTES, safe_name


def _multipart(filename: str, data: bytes) -> tuple[bytes, str]:
    boundary = "cleanmark-test-boundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    return body, f"multipart/form-data; boundary={boundary}"


@pytest.fixture()
def server_url():
    server = CleanmarkHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


def test_health(server_url):
    with urlopen(f"{server_url}/health") as response:
        payload = json.load(response)
        assert response.status == 200
        assert payload["ok"] is True
        assert response.headers["Cache-Control"] == "no-store"


def test_safe_name_reduces_paths_to_basename():
    assert safe_name("../../secret/notes.md") == "notes.md"
    assert safe_name(r"..\\secret\\notes.md") == "notes.md"
    assert safe_name("..") == "input"


def test_text_inspect_reports_hidden_character(server_url):
    body, content_type = _multipart("notes.txt", "hello\u200bworld".encode())
    request = Request(f"{server_url}/inspect", data=body, headers={"Content-Type": content_type}, method="POST")
    with urlopen(request) as response:
        payload = json.load(response)
        assert payload["kind"] == "text"
        assert payload["suspicious"] is True
        assert payload["report"]["findings"][0]["code_point"] == "U+200B"


def test_text_clean_returns_attachment(server_url):
    body, content_type = _multipart("notes.txt", "hello\u200bworld".encode())
    request = Request(f"{server_url}/clean", data=body, headers={"Content-Type": content_type}, method="POST")
    with urlopen(request) as response:
        assert response.read() == b"helloworld"
        assert response.headers["Content-Disposition"] == 'attachment; filename="notes.cleaned.txt"'
        report = json.loads(response.headers["X-Cleanmark-Report"])
        assert report["removed"] == 1


def test_unsupported_file_returns_415(server_url):
    body, content_type = _multipart("blob.bin", b"\x00\x01\x02\x03")
    connection = HTTPConnection(server_url.removeprefix("http://"))
    connection.request("POST", "/inspect", body=body, headers={"Content-Type": content_type})
    response = connection.getresponse()
    payload = json.loads(response.read())
    assert response.status == 415
    assert payload["error"]["code"] == "unsupported"
    connection.close()


def test_declared_oversize_request_returns_413(server_url):
    connection = HTTPConnection(server_url.removeprefix("http://"))
    connection.putrequest("POST", "/inspect")
    connection.putheader("Content-Type", "multipart/form-data; boundary=x")
    connection.putheader("Content-Length", str(MAX_FILE_BYTES + (1 << 20)))
    connection.endheaders()
    response = connection.getresponse()
    payload = json.loads(response.read())
    assert response.status == 413
    assert payload["error"]["code"] == "too-large"
    connection.close()
