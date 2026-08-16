# Cleanmark Web Cleaner — Design

Date: 2026-08-16
Status: Approved direction, implementation pending

## 1. Product goal

Cleanmark is an open-source, local-first web application for inspecting and cleaning hidden metadata, invisible text markers, and AI provenance data from content the user owns or is authorized to modify.

The project should be understandable and useful to non-technical users while remaining self-hostable and auditable.

Primary product promise:

- inspect before changing anything;
- keep simple text cleaning in the browser where practical;
- use a self-hosted server for complex file formats;
- require no account for the core workflow;
- make privacy and authorization expectations explicit.

Cleanmark is not positioned as a tool for removing visible creator logos or copyright watermarks.

## 2. MVP scope

The first release supports two workflows.

### Text workflow

Users can paste text into the browser and inspect for invisible or unusual Unicode characters. Cleaning happens locally in the browser without uploading the text.

Initial detections include:

- zero-width and invisible Unicode characters;
- unusual spacing characters;
- bidirectional control characters;
- tag characters and related hidden formatting markers.

The UI shows what was detected, how many characters are affected, and a cleaned preview before the user copies the result.

### File workflow

Users can upload a supported file, inspect it, then explicitly request a cleaned copy.

Initial formats:

- PNG
- JPEG
- WebP
- PDF
- DOCX
- TXT
- Markdown

Initial server-side cleaning targets:

- C2PA manifests and provenance metadata where supported;
- EXIF/XMP and related metadata;
- document properties and container metadata;
- Layer-A invisible-text cleanup inside supported text/document formats.

The first hosted/self-hosted release does not include heavyweight watermark-model backends such as CtrlRegen or reverse-SynthID scoring.

## 3. Architecture

Cleanmark uses a small monorepo with clear boundaries.

```text
cleanmark/
  apps/
    web/                 # Next.js + React web application
  services/
    cleaner/             # Python HTTP cleaning service
  packages/
    text-cleaner/        # framework-independent TypeScript local text cleaner
  docs/
  compose.yaml
  README.md
  LICENSE
  SECURITY.md
```

### Web application

Technology: Next.js, React, TypeScript.

Responsibilities:

- landing page and product explanation;
- text paste/inspect/clean UI;
- drag-and-drop file upload;
- inspect result presentation;
- explicit clean action;
- cleaned-file download;
- API proxy routes so browser clients never need a cleaner-service secret.

### Browser text-cleaner package

A small framework-independent TypeScript package contains deterministic text inspection and cleanup logic.

It must not depend on React. This keeps it testable, reusable, and suitable for future browser extensions or CLI wrappers.

### Cleaner service

Technology: Python.

Responsibilities:

- classify uploaded files;
- inspect supported file/container metadata;
- clean supported metadata and invisible text markers;
- invoke optional system tools such as `exiftool`, `qpdf`, and `c2patool` when available;
- return structured reports to the web application.

The service is not exposed directly to the public browser client in the default deployment.

## 4. API and data flow

User flow:

```text
Browser
  -> select/paste content
  -> Inspect
  -> review findings
  -> Clean
  -> preview/report
  -> Download or Copy
```

Text path:

```text
Browser UI -> packages/text-cleaner -> Browser UI
```

No server request is required for the default text workflow.

File path:

```text
Browser UI
  -> Next.js server route
  -> Python cleaner service
  -> Next.js server route
  -> Browser UI
```

The public-facing upload API should use `multipart/form-data` rather than base64 JSON. The web server may adapt this request to the cleaner service internally during the first implementation if needed.

MVP upload limit: 25 MiB per file.

## 5. Core screens

### Home / cleaner screen

One primary page with two modes:

- Paste Text
- Upload File

The page should communicate these principles without requiring a separate onboarding flow:

- Open source
- Local-first text cleaning
- No account required
- Inspect before cleaning
- Self-hostable

### Inspection state

The result must distinguish between:

- detected findings;
- informational metadata;
- unsupported or unavailable capabilities;
- no findings.

The UI must not claim that a file is definitively free of every possible watermark or provenance mechanism.

### Cleaned state

Show:

- successful/failed cleaning actions;
- a concise summary of removed or changed items;
- resulting file size where useful;
- a download button.

## 6. Safety and trust boundaries

Cleanmark should state that users should only process content they own or are authorized to modify.

The application should avoid language that promises evasion of attribution, moderation, fraud detection, or forensic systems.

The cleaner service must:

- sanitize uploaded filenames;
- enforce a strict upload/body size limit;
- process files in isolated temporary directories;
- avoid logging file contents;
- return generic internal-error messages to remote clients;
- run as an unprivileged user in the container;
- use no-store response headers for processed content;
- keep server credentials unavailable to browser JavaScript.

Uploaded files are ephemeral in the default deployment and are deleted after each request finishes.

## 7. Error handling

The web app should convert backend failures into user-facing categories:

- unsupported format;
- file too large;
- malformed/corrupt file;
- cleaner capability unavailable;
- cleaning failed;
- internal server error.

Errors should preserve the original file locally and never imply that a failed operation produced a safe cleaned output.

## 8. Testing strategy

### TypeScript

Unit tests cover:

- every supported invisible-character class;
- mixed normal/invisible Unicode input;
- no-op cleanup;
- deterministic reports;
- preservation of legitimate visible text.

### Python

Unit tests cover:

- file classification;
- filename sanitization;
- upload limits;
- supported metadata inspection;
- cleanup behavior using small fixtures;
- error responses.

### Web

Component/integration tests cover:

- paste -> inspect -> clean -> copy;
- upload -> inspect -> clean -> download;
- unsupported files;
- oversized files;
- service unavailable states.

### CI

GitHub Actions should run linting, type checks, and unit tests for both TypeScript and Python on pull requests and pushes to `main`.

## 9. Deployment

The default self-hosted path is Docker Compose.

```text
docker compose up --build
```

Default services:

- `web` — public web application;
- `cleaner` — private/internal Python service.

The cleaner service should not publish a host port in the production-oriented Compose configuration unless explicitly enabled for development.

## 10. Licensing and attribution

Cleanmark itself will use the MIT License.

If implementation code is adapted from `guillaumemeyer/watermarks-remover`, retain the applicable MIT copyright/license notice for copied or substantial derivative portions.

Optional third-party tools and model backends must be reviewed separately before distribution. The MVP deliberately excludes upstream components with unclear or non-commercial distribution constraints.

## 11. Non-goals for v0.1

The following are intentionally out of scope:

- user accounts;
- billing;
- persistent upload storage;
- batch processing;
- public API keys;
- visible logo/object removal from images;
- heavyweight ML watermark-removal backends;
- claims of universal watermark detection or removal.

## 12. Success criteria for v0.1

A user can:

1. paste text and locally inspect/clean supported invisible characters;
2. upload a supported file up to 25 MiB;
3. inspect findings before modification;
4. request cleaning explicitly;
5. download the cleaned file and see a clear action report;
6. run the complete application locally with Docker Compose;
7. understand from the README what Cleanmark does, what it does not do, and the authorization/privacy model.
