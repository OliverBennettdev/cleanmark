from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .files import CapabilityUnavailable, UnsupportedFormat, capabilities, clean_file, inspect_file

MAX_FILE_BYTES = 25 << 20
MAX_BODY_BYTES = MAX_FILE_BYTES + (512 << 10)
VERSION = os.environ.get("CLEANMARK_VERSION", "0.1.0-dev")


def safe_name(name: str) -> str:
    base = Path(name.replace("\\", "/")).name
    return "input" if base in {"", ".", ".."} else base


def cleaned_name(filename: str) -> str:
    path = Path(safe_name(filename))
    if path.suffix:
        return f"{path.stem}.cleaned{path.suffix}"
    return f"{path.name}.cleaned"


def _parse_content_disposition(value: str) -> dict[str, str]:
    parts = [part.strip() for part in value.split(";")]
    result: dict[str, str] = {}
    for part in parts[1:]:
        if "=" not in part:
            continue
        key, raw = part.split("=", 1)
        result[key.strip().lower()] = raw.strip().strip('"')
    return result


def parse_multipart(body: bytes, content_type: str) -> tuple[str, bytes]:
    marker = "boundary="
    if marker not in content_type:
        raise ValueError("missing multipart boundary")
    boundary = content_type.split(marker, 1)[1].split(";", 1)[0].strip().strip('"')
    if not boundary:
        raise ValueError("missing multipart boundary")
    delimiter = b"--" + boundary.encode("ascii", "strict")
    for part in body.split(delimiter):
        if part.startswith(b"--"):
            continue
        if part.startswith(b"\r\n"):
            part = part[2:]
        if not part:
            continue
        header_blob, separator, payload = part.partition(b"\r\n\r\n")
        if not separator:
            continue
        headers: dict[str, str] = {}
        for line in header_blob.decode("latin-1").split("\r\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()
        disposition = _parse_content_disposition(headers.get("content-disposition", ""))
        if disposition.get("name") != "file":
            continue
        filename = safe_name(disposition.get("filename", "input"))
        payload = payload.removesuffix(b"\r\n")
        if len(payload) > MAX_FILE_BYTES:
            raise OverflowError("file too large")
        return filename, payload
    raise ValueError("missing multipart file field")


class CleanmarkHTTPServer(ThreadingHTTPServer):
    daemon_threads = True


class Handler(BaseHTTPRequestHandler):
    server_version = f"Cleanmark/{VERSION}"

    def log_message(self, fmt: str, *args: object) -> None:
        # Request path/status are useful; bodies and filenames are deliberately not logged.
        print(f"cleanmark: {fmt % args}")

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _error(self, status: int, code: str, message: str) -> None:
        self._send_json(status, {"ok": False, "error": {"code": code, "message": message}})

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json(HTTPStatus.OK, {"ok": True, "version": VERSION})
        elif self.path == "/capabilities":
            self._send_json(HTTPStatus.OK, {"ok": True, "tools": capabilities()})
        else:
            self._error(HTTPStatus.NOT_FOUND, "not-found", "not found")

    def do_POST(self) -> None:  # noqa: N802
        if self.path not in {"/inspect", "/clean"}:
            self._error(HTTPStatus.NOT_FOUND, "not-found", "not found")
            return
        raw_length = self.headers.get("Content-Length", "")
        if not raw_length.isdigit():
            self._error(HTTPStatus.BAD_REQUEST, "malformed", "missing content length")
            return
        length = int(raw_length)
        if length > MAX_BODY_BYTES:
            self._error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "too-large", "file exceeds the 25 MiB limit")
            return
        content_type = self.headers.get("Content-Type", "")
        if not content_type.lower().startswith("multipart/form-data"):
            self._error(HTTPStatus.BAD_REQUEST, "malformed", "expected multipart/form-data")
            return
        try:
            body = self.rfile.read(length)
            filename, data = parse_multipart(body, content_type)
            if self.path == "/inspect":
                kind, report, suspicious = inspect_file(data, filename)
                self._send_json(
                    HTTPStatus.OK,
                    {"ok": True, "kind": kind, "suspicious": suspicious, "report": report},
                )
                return
            kind, cleaned, report = clean_file(data, filename)
            report_json = json.dumps(report, ensure_ascii=True, separators=(",", ":"))
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{cleaned_name(filename)}"')
            self.send_header("Content-Length", str(len(cleaned)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Cleanmark-Kind", kind)
            self.send_header("X-Cleanmark-Report", report_json)
            self.end_headers()
            self.wfile.write(cleaned)
        except OverflowError:
            self._error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "too-large", "file exceeds the 25 MiB limit")
        except UnsupportedFormat:
            self._error(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "unsupported", "unsupported file format")
        except CapabilityUnavailable as exc:
            self._error(HTTPStatus.SERVICE_UNAVAILABLE, "capability-unavailable", str(exc))
        except (UnicodeDecodeError, ValueError, OSError):
            self._error(HTTPStatus.BAD_REQUEST, "malformed", "file could not be processed")
        except Exception:
            self._error(HTTPStatus.INTERNAL_SERVER_ERROR, "internal", "internal server error")


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    server = CleanmarkHTTPServer((host, port), Handler)
    print(f"Cleanmark cleaner {VERSION} listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    serve(os.environ.get("CLEANMARK_HOST", "127.0.0.1"), int(os.environ.get("CLEANMARK_PORT", "8765")))
