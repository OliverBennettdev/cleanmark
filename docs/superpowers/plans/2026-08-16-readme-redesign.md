# Cleanmark README Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the root `README.md` with an English-first, product-first open-source landing page that is clearer, more trustworthy, and easier to self-host than the current README while staying accurate about Cleanmark v0.1.

**Architecture:** This is a documentation-only change. The implementation rewrites one public-facing file (`README.md`) around the approved content hierarchy, verifies every capability and command against the current repository, then performs a final copy/Markdown review before commit.

**Tech Stack:** GitHub-flavored Markdown, Docker Compose, pnpm workspace, Python 3.12 / pytest.

## Global Constraints

- Primary language: English.
- Hero positioning: **Open-source privacy cleaner for AI provenance & hidden metadata.**
- Hero secondary line: *Inspect and clean hidden AI marks from text and files.*
- Do not define Cleanmark as “the web UI for watermarks-remover” in the hero.
- Keep current capabilities and future roadmap visibly separate.
- Do not claim universal watermark/provenance detection or removal.
- Do not add fake screenshots, empty image boxes, or visible screenshot placeholders.
- Primary self-host path: `docker compose up --build`.
- Keep scope language: only process content the user owns or is authorized to modify.
- Do not market Cleanmark as a visible-logo remover or as a bypass tool for attribution, moderation, fraud detection, or forensic systems.
- Acknowledge `guillaumemeyer/watermarks-remover` near the end as upstream inspiration without implying affiliation or full parity.

---

### Task 1: Rewrite the root README as a product-first landing page

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: approved design in `docs/superpowers/specs/2026-08-16-readme-redesign-design.md`.
- Produces: root README sections in this exact order: Hero → Why Cleanmark → What Cleanmark can do today → Inspect before clean → Privacy by design → Quick Start → Architecture → Supported formats and capabilities → Roadmap → Contributing → Scope and responsible use → Acknowledgements → License.

- [ ] **Step 1: Replace the opening with the approved hero**

Use this opening copy exactly for the first three lines of content:

```markdown
# Cleanmark

**Open-source privacy cleaner for AI provenance & hidden metadata.**

*Inspect and clean hidden AI marks from text and files.*
```

Immediately follow it with a scan-friendly line containing these four properties:

```text
Local-first · Inspect before clean · No account required · Self-hostable
```

Then introduce the product with language equivalent to:

```markdown
Cleanmark helps you inspect hidden Unicode markers, document metadata, C2PA-related provenance data, and other supported signals before deciding what to remove from content you own or are authorized to modify.
```

- [ ] **Step 2: Add the product explanation and inspect-first workflow**

Write a concise `## Why Cleanmark` section covering:

- provenance/metadata tools are often CLI-first;
- Cleanmark exposes an inspect-first web workflow;
- pasted text can remain in-browser;
- file processing is self-hostable and ephemeral.

Add `## Inspect before clean` with this workflow:

```text
Drop or paste → Inspect → Review findings → Clean → Download or copy
```

State explicitly that selecting or uploading content does not itself trigger cleaning.

- [ ] **Step 3: Add the current-capability table**

Create `## What Cleanmark can do today` with a table covering only shipped v0.1 behavior:

```markdown
| Content | Inspect | Clean | Processing / requirements |
| --- | --- | --- | --- |
| Pasted text | Supported hidden Unicode classes | Supported hidden Unicode classes | Local in browser |
| TXT / Markdown | Supported hidden Unicode classes | Supported hidden Unicode classes | Server file workflow |
| DOCX | Document properties + supported hidden text | Supported document-property metadata + hidden text | Server |
| PNG / JPEG / WebP | Metadata and C2PA-related information when tooling is available | Metadata stripping when supported | Optional system tools |
| PDF | Metadata and C2PA-related information when tooling is available | Structural / metadata cleaning when supported | `qpdf` / `exiftool` where required |
```

Add a one-sentence caveat that “no findings” means no findings among mechanisms Cleanmark currently supports.

- [ ] **Step 4: Add the privacy/trust section**

Create `## Privacy by design` and state only implemented behavior:

- pasted-text inspection and cleaning run in the browser;
- no account is required for the core workflow;
- uploads are ephemeral by default;
- default Compose keeps the cleaner behind the web app;
- processed responses use `Cache-Control: no-store`;
- browser JavaScript does not receive cleaner-service credentials.

Do not use absolute phrases such as “fully private” or “zero data leaves your device,” because file workflows use the self-hosted cleaner service.

- [ ] **Step 5: Add Quick Start and local development**

Use this Quick Start verbatim:

```bash
git clone https://github.com/OliverBennettdev/cleanmark.git
cd cleanmark
docker compose up --build
```

Then state:

```markdown
Open `http://localhost:3000`.
```

Explain that the web app is published on port 3000 while the cleaner remains internal in the default Compose configuration.

Keep local-development requirements and commands concise:

```bash
pnpm install
pnpm --filter @cleanmark/web dev
```

and, in another terminal:

```bash
cd services/cleaner
CLEANMARK_HOST=127.0.0.1 CLEANMARK_PORT=8765 python -m cleaner.app
```

- [ ] **Step 6: Add the architecture section**

Use this diagram:

```text
Browser
  ├─ Local text inspection/cleaning
  │    └─ @cleanmark/text-cleaner
  │
  └─ File workflow
       └─ Next.js same-origin API
            └─ Python cleaner service
                 ├─ exiftool
                 ├─ qpdf
                 └─ c2patool
```

Follow with concise bullets explaining that text can stay client-side, file operations go through same-origin Next.js routes, and optional tools extend file capabilities.

- [ ] **Step 7: Add supported mechanisms, roadmap, contributing, scope, and acknowledgements**

In `## Supported formats and capabilities`, mention the current hidden-text classes:

- zero-width characters;
- soft hyphens;
- bidirectional controls;
- Unicode tag characters;
- unusual spacing characters.

State that supported unusual spaces are normalized to ASCII space and supported hidden controls are removed deterministically.

Use this roadmap structure:

```markdown
| Version | Focus | Status |
| --- | --- | --- |
| v0.1 | Web foundation | ✅ Shipped |
| v0.2 | Engine parity & upstream bridge | 🚧 Next |
| v0.3 | Better provenance inspection | Planned |
```

Describe v0.2 as future work including SVG/HTML/ODT, richer metadata reports, capability reporting, upstream-service compatibility, deeper C2PA inspection, and optional Layer B experiments subject to licensing/product boundaries.

For `## Contributing`, name useful areas: format support, cleaner adapters, UI/UX, test fixtures, documentation, security review.

Include these verification commands:

```bash
pnpm test
pnpm typecheck
pnpm lint

cd services/cleaner
python -m pytest -q
```

For `## Scope and responsible use`, include language equivalent to:

```markdown
Cleanmark is intended for privacy, hygiene, and provenance inspection on content you own or are authorized to modify. It is not designed for removing visible creator logos or for bypassing attribution, moderation, fraud-detection, or forensic systems.
```

For `## Acknowledgements`, include:

```markdown
Cleanmark was inspired in part by Guillaume Meyer's [`watermarks-remover`](https://github.com/guillaumemeyer/watermarks-remover), an MIT-licensed project that provides service and tooling for inspecting and cleaning AI provenance signals. Cleanmark is an independent project focused on a web-first, inspect-before-clean experience.
```

Add a note that future copied/substantially derived MIT code must retain applicable copyright and permission notices.

Finish with `## License` linking to `LICENSE`.

- [ ] **Step 8: Review the rewritten README against the design**

Verify all required headings are present and in the approved order. Confirm the hero does not mention `watermarks-remover`, there is no screenshot placeholder, no unsupported format is presented as shipped, and roadmap wording remains future-tense.

- [ ] **Step 9: Commit the README rewrite**

```bash
git add README.md
git commit -m "docs: redesign Cleanmark README"
```

---

### Task 2: Verify README claims against the current repository

**Files:**
- Read: `compose.yaml`
- Read: `apps/web/lib/cleaner-api.ts`
- Read: `packages/text-cleaner/src/index.ts`
- Read: `services/cleaner/cleaner/app.py`
- Read: `services/cleaner/cleaner/files.py`
- Read: `.github/workflows/ci.yml`
- Modify only if needed: `README.md`

**Interfaces:**
- Consumes: README from Task 1 and current implementation files.
- Produces: README wording whose operational, privacy, format, and test claims match the repository.

- [ ] **Step 1: Verify deployment and trust-boundary claims**

Check that `compose.yaml` exposes the web service while keeping the cleaner internal, and confirm the README does not claim a public cleaner endpoint by default.

- [ ] **Step 2: Verify upload and cache claims**

Check `apps/web/lib/cleaner-api.ts` and `services/cleaner/cleaner/app.py` for the 25 MiB limit, same-origin proxy behavior, `no-store`, and generic service errors. Adjust README wording if any claim is broader than implementation.

- [ ] **Step 3: Verify hidden-text behavior**

Check `packages/text-cleaner/src/index.ts` for the exact hidden-character classes and unusual-space normalization behavior. Remove or reword any class not actually implemented.

- [ ] **Step 4: Verify file-format claims**

Check `services/cleaner/cleaner/files.py` and format classification code to confirm TXT/Markdown, DOCX, PNG/JPEG/WebP, and PDF behavior. Ensure SVG/HTML/ODT appear only in the roadmap.

- [ ] **Step 5: Verify contributor commands**

Check root `package.json`, workspace package scripts, Python project files, and `.github/workflows/ci.yml` to confirm:

```bash
pnpm test
pnpm typecheck
pnpm lint
cd services/cleaner && python -m pytest -q
```

are valid project commands.

- [ ] **Step 6: Commit any factual corrections**

If verification required changes:

```bash
git add README.md
git commit -m "docs: align README claims with implementation"
```

If no changes are needed, do not create an empty commit.

---

### Task 3: Final README quality gate

**Files:**
- Review: `README.md`
- Review: `docs/superpowers/specs/2026-08-16-readme-redesign-design.md`

**Interfaces:**
- Consumes: fact-checked README.
- Produces: publication-ready root README.

- [ ] **Step 1: Run a claims scan**

Search the README for risky/unwanted phrasing and ensure none is used as a product claim:

```text
remove any watermark
all watermarks
fully private
guaranteed clean
undetectable
bypass
```

`bypass` may appear only in the responsible-use sentence stating what Cleanmark is not for.

- [ ] **Step 2: Run a roadmap/current-state separation scan**

Confirm SVG, HTML, ODT, Layer B, engine parity, and upstream adapter work appear only as planned/future work.

- [ ] **Step 3: Run a usability scan**

Confirm a first-time reader can find, without reading source code:

- what Cleanmark is;
- the inspect-first workflow;
- current format support;
- privacy model;
- the three-command Docker Quick Start;
- architecture;
- roadmap;
- contribution test commands;
- upstream acknowledgement.

- [ ] **Step 4: Check Markdown structure**

Verify heading levels are consistent, fenced code blocks are closed, tables have matching column counts, and internal links point to existing repository files (`LICENSE`, `SECURITY.md`).

- [ ] **Step 5: Commit final polish if needed**

If the quality gate finds copy/Markdown issues:

```bash
git add README.md
git commit -m "docs: polish README"
```

If no changes are needed, do not create an empty commit.
