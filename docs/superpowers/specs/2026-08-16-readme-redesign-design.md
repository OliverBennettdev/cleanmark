# Cleanmark README Redesign — Design

Date: 2026-08-16
Status: Approved direction, implementation pending

## 1. Goal

Rewrite the root `README.md` so it works as Cleanmark's primary open-source landing page: clear enough for first-time visitors, trustworthy about current capabilities, quick to self-host, and useful to contributors.

The README should be materially better than a conventional feature-dump or developer-first README by combining product clarity with technical credibility.

Success means a visitor can understand within roughly one minute:

- what Cleanmark is;
- what it can and cannot do today;
- why the inspect-before-clean workflow matters;
- how privacy is handled;
- how to run it locally;
- where the project is heading;
- how it relates to upstream inspiration without presenting Cleanmark as merely a wrapper.

## 2. Audience and language

Primary language: English.

Primary audiences:

1. users who want a self-hostable web interface for provenance and metadata inspection;
2. developers evaluating the architecture or deployment model;
3. open-source contributors looking for a concrete place to help.

A future `README.zh-CN.md` may provide a Chinese translation, but this redesign only changes the English root README.

## 3. Positioning

Primary positioning:

> **Open-source privacy cleaner for AI provenance & hidden metadata.**

Secondary line:

> *Inspect and clean hidden AI marks from text and files.*

The README must keep Cleanmark's brand independent. It must not describe Cleanmark in the hero as “the web UI for watermarks-remover.”

The upstream project is acknowledged later in the document.

## 4. Hero design

The opening section should be compact and product-first.

Required opening copy:

```markdown
# Cleanmark

**Open-source privacy cleaner for AI provenance & hidden metadata.**

*Inspect and clean hidden AI marks from text and files.*
```

Immediately below, communicate four product properties in a scan-friendly line or badges:

- Local-first
- Inspect before clean
- No account required
- Self-hostable

The first explanatory paragraph should say, in substance:

> Cleanmark helps you inspect hidden Unicode markers, document metadata, C2PA-related provenance data, and other supported signals before deciding what to remove from content you own or are authorized to modify.

The wording must not imply universal detection or removal.

## 5. Content strategy

The README follows a product-first open-source structure:

1. Hero
2. Why Cleanmark
3. What Cleanmark can do today
4. Inspect before clean
5. Privacy by design
6. Quick Start
7. Architecture
8. Supported formats and capabilities
9. Roadmap
10. Contributing
11. Scope and responsible use
12. Acknowledgements
13. License

The top half should optimize for comprehension and trust. The lower half should provide enough engineering detail for self-hosters and contributors without overwhelming the first-time reader.

## 6. Why Cleanmark

This section should explain the product gap concisely:

- many provenance and metadata tools are CLI-first;
- Cleanmark provides an inspect-first web workflow;
- pasted text can stay entirely in the browser;
- file processing is self-hostable and ephemeral;
- users review findings before asking Cleanmark to modify a file.

Avoid competitive or dismissive language about other projects.

## 7. Current capabilities

The README must distinguish shipped functionality from planned work.

Use a capability table that communicates both support and dependencies.

Current v0.1 coverage:

| Content | Inspect | Clean | Notes |
| --- | --- | --- | --- |
| Pasted text | hidden Unicode classes | hidden Unicode classes | local in browser |
| TXT / Markdown | hidden Unicode classes | hidden Unicode classes | server file workflow |
| DOCX | document properties + supported hidden text | remove supported document-property metadata + hidden text | server |
| PNG / JPEG / WebP | metadata / C2PA-related information when tooling is available | metadata stripping when supported | optional system tools |
| PDF | metadata / C2PA-related information when tooling is available | structural/metadata cleaning when supported | `qpdf` / `exiftool` where required |

The README should use status language such as:

- `Supported`
- `Requires optional tool`
- `Planned`

Do not claim that “no findings” proves a file contains no watermark or provenance mechanism.

## 8. Inspect-before-clean workflow

Present the primary workflow as a short sequence:

```text
Drop or paste → Inspect → Review findings → Clean → Download or copy
```

The copy should emphasize that selecting or uploading content does not itself trigger cleaning.

This is a core product differentiator and should appear before installation instructions.

## 9. Privacy by design

Create a dedicated trust section covering:

- pasted-text inspection and cleaning run locally in the browser;
- no account is required for the core workflow;
- file uploads are ephemeral by default;
- the Python cleaner remains behind the web application in the default Compose deployment;
- processed-content responses use `Cache-Control: no-store`;
- browser JavaScript does not receive cleaner-service credentials;
- users should only process content they own or are authorized to modify.

Keep security claims limited to behavior implemented by the current project.

## 10. Quick Start

The shortest supported path should be prominent and copy-pasteable:

```bash
git clone https://github.com/OliverBennettdev/cleanmark.git
cd cleanmark
docker compose up --build
```

Then:

> Open `http://localhost:3000`.

The README should explain that the default Compose configuration exposes the web application while keeping the cleaner service on the internal network.

Detailed local-development commands belong after Quick Start, not before it.

## 11. Architecture

Use a compact text diagram:

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

Follow the diagram with a short explanation of the trust boundary:

- simple text work stays client-side;
- file operations go through same-origin Next.js routes;
- the browser does not connect directly to the cleaner service;
- optional system tools extend format-specific capabilities.

## 12. Screenshot policy

Do not add a fake screenshot, mock screenshot, empty image box, or visible placeholder to the README.

The first rewritten README must be complete without imagery. A real product screenshot or demo GIF may be added later once there is an asset worth maintaining.

## 13. Roadmap

Keep the roadmap short and credible.

Required high-level stages:

```text
v0.1  Web foundation                  ✅
v0.2  Engine parity & upstream bridge 🚧
v0.3  Better provenance inspection    Planned
```

The v0.2 description should mention:

- SVG / HTML / ODT support;
- richer metadata reports;
- cleaner capability reporting;
- upstream-service adapter / compatibility work;
- deeper C2PA inspection;
- optional Layer B experiments where licensing and product boundaries permit.

Roadmap items must be clearly labeled as future work, not current support.

## 14. Contributing

The contributing section should tell people where help is useful rather than using generic open-source boilerplate.

Priority contribution areas:

- format support;
- cleaner adapters;
- UI/UX improvements;
- test fixtures;
- documentation;
- security review.

Include the current verification commands:

```bash
pnpm test
pnpm typecheck
pnpm lint

cd services/cleaner
python -m pytest -q
```

Do not invent a contribution policy that the repository does not yet have.

## 15. Scope and responsible use

Include a concise statement equivalent to:

> Cleanmark is intended for privacy, hygiene, and provenance inspection on content you own or are authorized to modify. It is not designed for removing visible creator logos or for bypassing attribution, moderation, fraud-detection, or forensic systems.

The README must avoid language that markets the project as an evasion tool.

## 16. Acknowledgements and upstream relationship

Do not mention `watermarks-remover` in the hero.

Near the end, include a clear acknowledgement along these lines:

> Cleanmark was inspired in part by Guillaume Meyer's `watermarks-remover`, an MIT-licensed project that provides service and tooling for inspecting and cleaning AI provenance signals. Cleanmark is an independent project focused on a web-first, inspect-before-clean experience.

If future implementation copies or substantially derives code from that project, retain the applicable MIT copyright and permission notice for those portions.

Avoid implying endorsement, official affiliation, or full feature parity.

## 17. Tone and writing rules

The README should feel like a mature open-source product rather than marketing copy.

Rules:

- short paragraphs and strong headings;
- concrete statements before abstractions;
- no inflated claims such as “remove any watermark” or “fully private”;
- no unexplained jargon in the first screen;
- technical terminology is acceptable after the product is understood;
- prefer direct verbs: inspect, review, clean, run, contribute;
- keep current capabilities and future roadmap visibly separate;
- use tables only where they genuinely improve scanning;
- avoid decorative ASCII art that pushes useful information below the fold.

## 18. Definition of done

The README redesign is complete when:

1. the first screen communicates the agreed Cleanmark positioning and four core properties;
2. a new visitor can identify current capabilities and limitations without reading source code;
3. the inspect-before-clean model is obvious;
4. privacy and authorization boundaries are explicit;
5. `docker compose up --build` is presented as the primary self-host path;
6. architecture is understandable from one compact diagram;
7. roadmap work is separated from shipped functionality;
8. contributor entry points and test commands are included;
9. upstream inspiration is acknowledged without defining Cleanmark as a wrapper;
10. no screenshot placeholder or unsupported capability claim appears in the document.
