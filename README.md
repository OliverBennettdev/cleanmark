# Cleanmark

**Inspect hidden text markers and file metadata before deciding what to clean.**

Cleanmark is an open-source, local-first web application for privacy hygiene on content you own or are authorized to modify. Pasted text can be inspected and cleaned entirely in the browser. Files use a small self-hostable Python service and are processed ephemerally.

> Cleanmark does not claim universal watermark detection or removal. It is not a visible-logo/object removal tool, and v0.1 intentionally excludes heavyweight ML watermark-removal backends.

## v0.1 capabilities

| Workflow | Inspect | Clean | Processing |
| --- | --- | --- | --- |
| TXT / Markdown | Hidden Unicode classes | Hidden Unicode classes | Browser for pasted text; server for files |
| DOCX | Document properties + hidden text in Word XML | Remove document-property parts/references + Layer-A hidden text | Server |
| PNG / JPEG / WebP | Metadata / C2PA when tools are available | Metadata stripping with `exiftool` | Server |
| PDF | Metadata / C2PA when tools are available | Structural rewrite with `qpdf` + metadata stripping with `exiftool` | Server |

Supported hidden-text classes include zero-width characters, soft hyphens, bidirectional controls, Unicode tag characters, and unusual spacing characters. Cleanmark normalizes supported unusual spaces to an ASCII space and removes supported hidden controls deterministically.

## Product principles

- **Inspect first.** Selecting a file never modifies it.
- **Local-first.** The default paste-text workflow does not need a server request.
- **No account.** The core workflow has no authentication/account requirement.
- **Ephemeral uploads.** The cleaner works in request-scoped temporary storage and does not persist uploads by default.
- **Self-hostable.** Docker Compose exposes only the web application; the cleaner stays on the internal network.
- **Scoped claims.** A “no findings” result means no findings among the mechanisms Cleanmark currently supports.

## Run with Docker

```bash
docker compose up --build
```

Open `http://localhost:3000`.

The default Compose stack publishes only the web port. The cleaner is reachable from the web container at `http://cleaner:8765` but is not mapped to a host port.

## Local development

Requirements:

- Node.js 22+
- pnpm 9.15+
- Python 3.12+
- pytest for Python tests
- optional `exiftool` and `qpdf` for image/PDF cleaning
- optional `c2patool` for C2PA inspection

Install JavaScript dependencies:

```bash
pnpm install
```

Run the web app:

```bash
pnpm --filter @cleanmark/web dev
```

In another terminal, run the cleaner:

```bash
cd services/cleaner
CLEANMARK_HOST=127.0.0.1 CLEANMARK_PORT=8765 python -m cleaner.app
```

The web server defaults to `http://127.0.0.1:8765` outside Docker. Override with the server-only `CLEANER_SERVICE_URL` environment variable when needed.

## Tests

```bash
pnpm test
pnpm typecheck
pnpm lint

cd services/cleaner
python -m pytest -q
```

The browser-local text package also has no runtime dependencies and its logic tests can run directly on Node 22's TypeScript type stripping:

```bash
node --experimental-strip-types --test packages/text-cleaner/src/index.test.ts
```

## Repository layout

```text
apps/web/                Next.js + React web application and same-origin proxy routes
packages/text-cleaner/   framework-independent TypeScript inspect/clean engine
services/cleaner/        Python HTTP service and file adapters
docs/superpowers/        product design and implementation plan
```

## API shape

The cleaner exposes an internal HTTP API:

- `GET /health`
- `GET /capabilities`
- `POST /inspect` — `multipart/form-data` with a `file` field; JSON findings response
- `POST /clean` — `multipart/form-data` with a `file` field; cleaned bytes response

The public web app proxies these requests through same-origin Next.js route handlers. The v0.1 upload limit is **25 MiB per file** at both proxy and cleaner boundaries.

## Security and authorization

Only process content you own or are authorized to modify. Cleanmark is intended for privacy, hygiene, and provenance inspection—not for bypassing attribution, moderation, fraud-detection, or forensic systems.

The cleaner sanitizes uploaded filenames, enforces request limits, uses isolated temporary directories for complex file work, avoids logging file contents, sends `Cache-Control: no-store`, and returns generic internal errors to remote clients.

See [SECURITY.md](SECURITY.md) for vulnerability reporting guidance.

## Attribution and third-party tools

Cleanmark itself is MIT licensed. If future changes copy or substantially derive implementation code from another MIT-licensed project, retain the applicable copyright and permission notice for those portions.

Optional tools and model backends require their own license review before distribution. v0.1 deliberately excludes components with unclear or non-commercial distribution constraints.

## License

[MIT](LICENSE)
