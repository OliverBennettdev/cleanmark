# Cleanmark v0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a working open-source Cleanmark v0.1 that locally inspects/cleans hidden Unicode text and server-side inspects/cleans supported files through a Next.js web UI and Python cleaner service.

**Architecture:** Use a small monorepo. `packages/text-cleaner` contains framework-independent TypeScript logic used directly in the browser. `apps/web` contains the Next.js UI plus same-origin proxy routes. `services/cleaner` contains a Python HTTP service that owns file inspection/cleaning and may call system tools such as `exiftool`, `qpdf`, and `c2patool` when installed. Docker Compose runs `web` publicly and `cleaner` only on the internal network.

**Tech Stack:** Node.js 22+, pnpm 9+, Next.js 15, React 19, TypeScript 5, Vitest, Python 3.12+, pytest, Docker Compose, GitHub Actions.

## Global Constraints

- Cleanmark is open source under the MIT License.
- Text inspection/cleaning is local-first and must not require a server request.
- File workflow is inspect first, then explicit clean.
- MVP formats: PNG, JPEG, WebP, PDF, DOCX, TXT, Markdown.
- Public upload limit: 25 MiB per file.
- No accounts, billing, persistent upload storage, batch processing, visible-logo removal, or heavyweight ML watermark-removal backends in v0.1.
- The product must say users should process only content they own or are authorized to modify.
- The UI must not claim universal watermark detection/removal.
- Uploaded files are ephemeral and must be deleted after each request.
- Browser JavaScript must never receive cleaner-service credentials.

---

## File Structure

```text
cleanmark/
  .github/workflows/ci.yml          # TS/Python CI
  apps/web/
    app/
      api/clean/route.ts            # same-origin clean proxy
      api/inspect/route.ts          # same-origin inspect proxy
      globals.css                   # visual system
      layout.tsx                    # metadata + root layout
      page.tsx                      # single-screen cleaner experience
    components/
      file-cleaner.tsx              # upload/inspect/clean/download state machine
      text-cleaner.tsx              # paste/inspect/clean/copy state machine
    lib/cleaner-api.ts              # server-only cleaner client
    package.json
    tsconfig.json
    vitest.config.ts
  packages/text-cleaner/
    src/index.ts                    # public inspectText / cleanText API
    src/index.test.ts               # deterministic Unicode tests
    package.json
    tsconfig.json
  services/cleaner/
    cleaner/
      __init__.py
      app.py                        # HTTP server + routing
      classify.py                   # format detection
      models.py                     # report/result dataclasses
      text.py                       # Unicode inspect/clean
      files.py                      # image/container inspection/clean adapters
    tests/
      test_app.py
      test_classify.py
      test_text.py
    Dockerfile
    pyproject.toml
  .dockerignore
  .gitignore
  compose.yaml
  LICENSE
  README.md
  SECURITY.md
  package.json                      # pnpm workspace scripts
  pnpm-workspace.yaml
```

---

### Task 1: Repository foundation and workspace

**Files:**
- Create: `package.json`
- Create: `pnpm-workspace.yaml`
- Create: `.gitignore`
- Create: `.dockerignore`
- Create: `LICENSE`
- Create: `README.md`
- Create: `SECURITY.md`

**Interfaces:**
- Produces root commands `pnpm test`, `pnpm lint`, and `pnpm typecheck` for later CI.

- [ ] **Step 1: Create workspace manifests**

`package.json`:

```json
{
  "name": "cleanmark",
  "private": true,
  "packageManager": "pnpm@9.15.4",
  "scripts": {
    "test": "pnpm -r test",
    "lint": "pnpm -r lint",
    "typecheck": "pnpm -r typecheck"
  }
}
```

`pnpm-workspace.yaml`:

```yaml
packages:
  - apps/*
  - packages/*
```

- [ ] **Step 2: Add ignore files and MIT license**

Ignore Node, Python, coverage, environment, and build output. License text must be the standard MIT License with `Copyright (c) 2026 Cleanmark contributors`.

- [ ] **Step 3: Add initial README and SECURITY**

README must state: local-first text cleaning, inspect-before-clean workflow, self-hosting, supported MVP formats, authorization-only use, and non-goals. SECURITY must instruct users not to include sensitive file contents in vulnerability reports.

- [ ] **Step 4: Verify repository docs render and workspace YAML parses**

Run:

```bash
python - <<'PY'
from pathlib import Path
assert 'packages:' in Path('pnpm-workspace.yaml').read_text()
assert 'MIT License' in Path('LICENSE').read_text()
PY
```

Expected: exit 0.

- [ ] **Step 5: Commit**

```bash
git add package.json pnpm-workspace.yaml .gitignore .dockerignore LICENSE README.md SECURITY.md
git commit -m "chore: bootstrap Cleanmark workspace"
```

---

### Task 2: Browser-local text cleaner package

**Files:**
- Create: `packages/text-cleaner/package.json`
- Create: `packages/text-cleaner/tsconfig.json`
- Create: `packages/text-cleaner/src/index.test.ts`
- Create: `packages/text-cleaner/src/index.ts`

**Interfaces:**
- Produces:
  - `inspectText(input: string): TextInspection`
  - `cleanText(input: string): CleanTextResult`
  - `TextFinding = { codePoint: string; char: string; index: number; category: FindingCategory; label: string }`
  - `TextInspection = { suspicious: boolean; findings: TextFinding[]; counts: Record<FindingCategory, number> }`
  - `CleanTextResult = { text: string; inspection: TextInspection; removed: number }`

- [ ] **Step 1: Write failing Unicode inspection tests**

Tests must cover `U+200B ZERO WIDTH SPACE`, `U+00AD SOFT HYPHEN`, `U+202E RIGHT-TO-LEFT OVERRIDE`, `U+E0001 LANGUAGE TAG`, `U+00A0 NO-BREAK SPACE`, normal multilingual text, and deterministic indexes.

Example:

```ts
import { describe, expect, it } from "vitest";
import { cleanText, inspectText } from "./index";

it("finds and removes zero-width space", () => {
  const input = "hello\u200bworld";
  expect(inspectText(input).findings[0]).toMatchObject({ codePoint: "U+200B", index: 5 });
  expect(cleanText(input).text).toBe("helloworld");
});

it("preserves ordinary CJK text", () => {
  expect(cleanText("你好，世界").text).toBe("你好，世界");
});
```

- [ ] **Step 2: Run test to verify failure**

Run: `pnpm --dir packages/text-cleaner test`

Expected: FAIL because implementation does not exist.

- [ ] **Step 3: Implement minimal deterministic inspector/cleaner**

Use explicit character classes rather than heuristic rewriting. Categories: `zero-width`, `soft-hyphen`, `bidi-control`, `tag`, `unusual-space`. Replace unusual spaces with a normal ASCII space; remove the other supported hidden controls.

- [ ] **Step 4: Run tests and typecheck**

Run:

```bash
pnpm --dir packages/text-cleaner test
pnpm --dir packages/text-cleaner typecheck
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add packages/text-cleaner
git commit -m "feat: add local text cleaner"
```

---

### Task 3: Python cleaner core

**Files:**
- Create: `services/cleaner/pyproject.toml`
- Create: `services/cleaner/cleaner/__init__.py`
- Create: `services/cleaner/cleaner/models.py`
- Create: `services/cleaner/cleaner/classify.py`
- Create: `services/cleaner/cleaner/text.py`
- Create: `services/cleaner/tests/test_classify.py`
- Create: `services/cleaner/tests/test_text.py`

**Interfaces:**
- Produces:
  - `classify_bytes(data: bytes, filename: str) -> Literal['text','image','container','unsupported']`
  - `inspect_text(text: str) -> dict[str, object]`
  - `clean_text(text: str) -> tuple[str, dict[str, object]]`

- [ ] **Step 1: Write failing classifier tests**

Use tiny byte fixtures for PNG magic, JPEG magic, PDF magic, ZIP/DOCX magic, UTF-8 Markdown, and unknown binary.

- [ ] **Step 2: Run classifier tests and confirm failure**

Run: `cd services/cleaner && python -m pytest tests/test_classify.py -q`

Expected: FAIL due missing module/functions.

- [ ] **Step 3: Implement conservative magic/extension classification**

Supported extensions are `.png`, `.jpg`, `.jpeg`, `.webp`, `.pdf`, `.docx`, `.txt`, `.md`, `.markdown`. Unknown binary is `unsupported` rather than guessed as text.

- [ ] **Step 4: Write failing Python text-cleaner parity tests**

Use the same representative Unicode cases as Task 2 so browser/server behavior stays aligned for supported character classes.

- [ ] **Step 5: Implement Python text inspection/cleaning and run tests**

Run: `cd services/cleaner && python -m pytest tests/test_classify.py tests/test_text.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add services/cleaner
git commit -m "feat: add cleaner core"
```

---

### Task 4: File adapters and cleaner HTTP API

**Files:**
- Create: `services/cleaner/cleaner/files.py`
- Create: `services/cleaner/cleaner/app.py`
- Create: `services/cleaner/tests/test_app.py`

**Interfaces:**
- Consumes Task 3 classification/text functions.
- Produces HTTP endpoints:
  - `GET /health`
  - `GET /capabilities`
  - `POST /inspect` with multipart field `file`
  - `POST /clean` with multipart field `file`
- Success JSON for inspect: `{ ok, kind, suspicious, report }`
- Clean response: cleaned bytes with `Content-Disposition: attachment` and `X-Cleanmark-Report` containing compact JSON.

- [ ] **Step 1: Write failing API tests**

Tests must prove: health works; 25 MiB limit rejects oversized declared requests; unsupported files return 415; filenames are reduced to basenames; text inspect reports findings; text clean returns cleaned bytes; internal exceptions do not expose stack traces.

- [ ] **Step 2: Run API tests and confirm failure**

Run: `cd services/cleaner && python -m pytest tests/test_app.py -q`

Expected: FAIL.

- [ ] **Step 3: Implement stdlib HTTP server with multipart parsing boundary**

Use isolated `TemporaryDirectory` per request, `Cache-Control: no-store`, generic 500 errors, and 25 MiB decoded-file cap. Do not log body/file contents.

- [ ] **Step 4: Implement file adapters**

MVP behavior:
- TXT/Markdown: deterministic Unicode inspect/clean.
- PNG/JPEG/WebP: inspect basic metadata using available tools; clean metadata with `exiftool` when installed, otherwise return a capability-unavailable error rather than silently claiming success.
- PDF: require `qpdf` for structural rewrite; optionally run `exiftool` for metadata stripping.
- DOCX: rebuild ZIP while removing known document-property parts/fields and clean text-bearing XML with Layer-A text cleanup without changing arbitrary binary parts.

- [ ] **Step 5: Run Python suite**

Run: `cd services/cleaner && python -m pytest -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add services/cleaner
git commit -m "feat: expose cleaner HTTP API"
```

---

### Task 5: Next.js application shell and text workflow

**Files:**
- Create: `apps/web/package.json`
- Create: `apps/web/tsconfig.json`
- Create: `apps/web/next.config.ts`
- Create: `apps/web/vitest.config.ts`
- Create: `apps/web/app/layout.tsx`
- Create: `apps/web/app/globals.css`
- Create: `apps/web/app/page.tsx`
- Create: `apps/web/components/text-cleaner.tsx`
- Create: `apps/web/components/text-cleaner.test.tsx`

**Interfaces:**
- Consumes `@cleanmark/text-cleaner` from Task 2.
- Produces a single-page UI with mode tabs `Paste text` and `Upload file`.

- [ ] **Step 1: Write failing component test for paste -> inspect -> clean**

Test with `hello\u200bworld`: initial state explains local processing; Inspect shows one finding; Clean shows `helloworld`; Copy action becomes available.

- [ ] **Step 2: Run test and confirm failure**

Run: `pnpm --dir apps/web test`

Expected: FAIL.

- [ ] **Step 3: Implement visual shell and text workflow**

Requirements:
- one focused cleaner page, not a dashboard;
- strong drag/paste focal area;
- trust badges for `Open source`, `Local-first`, `No account`, `Inspect first`;
- clear local-processing copy for text;
- no claim that all watermark mechanisms can be detected;
- responsive from 360 px upward.

- [ ] **Step 4: Run tests/typecheck**

Run:

```bash
pnpm --dir apps/web test
pnpm --dir apps/web typecheck
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web
git commit -m "feat: add Cleanmark web text workflow"
```

---

### Task 6: Web file proxy and file workflow

**Files:**
- Create: `apps/web/lib/cleaner-api.ts`
- Create: `apps/web/app/api/inspect/route.ts`
- Create: `apps/web/app/api/clean/route.ts`
- Create: `apps/web/components/file-cleaner.tsx`
- Create: `apps/web/components/file-cleaner.test.tsx`

**Interfaces:**
- Server-only env: `CLEANER_SERVICE_URL`, default `http://cleaner:8765` in Compose.
- Browser only calls same-origin `/api/inspect` and `/api/clean`.

- [ ] **Step 1: Write failing proxy tests**

Prove 25 MiB validation happens before forwarding, upstream status codes map to stable browser-safe errors, and no cleaner credential is serialized to client code.

- [ ] **Step 2: Implement server-only cleaner client and route handlers**

Forward multipart bodies to cleaner. Add `Cache-Control: no-store`. Preserve attachment filename for successful clean responses.

- [ ] **Step 3: Write failing file-workflow component test**

Mock `/api/inspect` and `/api/clean`. Prove Upload -> Inspect -> findings -> explicit Clean -> Download. Cleaning button must not appear as already completed after inspection.

- [ ] **Step 4: Implement file workflow UI**

States: idle, inspecting, inspected, cleaning, cleaned, error. Error categories: unsupported, too-large, malformed, capability-unavailable, cleaning-failed, internal.

- [ ] **Step 5: Run full web suite**

Run:

```bash
pnpm --dir apps/web test
pnpm --dir apps/web typecheck
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add apps/web
git commit -m "feat: add file inspect and clean workflow"
```

---

### Task 7: Containers and self-hosting

**Files:**
- Create: `apps/web/Dockerfile`
- Create: `services/cleaner/Dockerfile`
- Create: `compose.yaml`

**Interfaces:**
- Public service: `web` on host port `3000`.
- Internal-only service: `cleaner:8765`; no host port in default Compose.

- [ ] **Step 1: Add cleaner Dockerfile**

Use Python 3.12 slim, create an unprivileged `cleanmark` user, install `exiftool`, `qpdf`, and `c2patool` only where licensing/distribution permits in the chosen base image, copy service code, expose 8765 internally, run as non-root.

- [ ] **Step 2: Add web Dockerfile**

Use Node 22 multi-stage build with pnpm. Production stage runs as non-root.

- [ ] **Step 3: Add Compose network**

`web` depends on `cleaner`, passes `CLEANER_SERVICE_URL=http://cleaner:8765`, publishes only `3000:3000`, and gives cleaner a temporary writable `/tmp` while otherwise keeping filesystem permissions minimal.

- [ ] **Step 4: Validate Compose**

Run:

```bash
docker compose config
docker compose build
```

Expected: both commands exit 0.

- [ ] **Step 5: Smoke test**

Run stack, then verify `GET http://localhost:3000` returns 200 and the web proxy can inspect a small text fixture.

- [ ] **Step 6: Commit**

```bash
git add apps/web/Dockerfile services/cleaner/Dockerfile compose.yaml
git commit -m "chore: add self-hosted containers"
```

---

### Task 8: CI, documentation, and release-quality verification

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `README.md`
- Modify: `SECURITY.md`

**Interfaces:**
- Produces required CI jobs: `typescript` and `python`.

- [ ] **Step 1: Add GitHub Actions CI**

TypeScript job: Node 22, pnpm 9.15.4, install frozen lockfile, run `pnpm test`, `pnpm typecheck`, `pnpm lint` when lint scripts exist.

Python job: Python 3.12, install `services/cleaner` dev dependencies, run `pytest -q`.

- [ ] **Step 2: Expand README with exact local commands**

Include:

```bash
pnpm install
pnpm test
cd services/cleaner && python -m pytest -q

docker compose up --build
```

Document supported formats, 25 MiB limit, local-only text behavior, ephemeral uploads, optional system-tool capabilities, and attribution obligations for any future copied upstream MIT code.

- [ ] **Step 3: Run complete local verification**

Run:

```bash
pnpm install
pnpm test
pnpm typecheck
cd services/cleaner && python -m pytest -q
cd ../..
docker compose config
```

Expected: all exit 0.

- [ ] **Step 4: Review against spec**

Confirm every v0.1 success criterion in `docs/superpowers/specs/2026-08-16-cleanmark-web-cleaner-design.md` is represented by a passing workflow/test or documented manual smoke test.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/ci.yml README.md SECURITY.md
git commit -m "ci: verify Cleanmark v0.1"
```

---

## Plan Self-Review

- Spec coverage: all architecture, workflows, safety boundaries, testing, deployment, licensing, non-goals, and v0.1 success criteria map to Tasks 1-8.
- Placeholder scan: no implementation step relies on TBD/TODO placeholders.
- Type consistency: browser text API is fixed in Task 2; cleaner HTTP contract is fixed in Task 4; web proxy consumes that contract in Task 6.
- Scope: one MVP; heavy ML backends, accounts, persistence, batch processing, and visible logo removal remain explicitly excluded.
