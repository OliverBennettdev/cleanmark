import { CleanerWorkspace } from "@/components/cleaner-workspace";

const principles = ["Open source", "Local-first text", "No account", "Inspect first"];

export default function Home() {
  return (
    <main className="page-shell">
      <nav className="topbar" aria-label="Primary">
        <a className="brand" href="#top" aria-label="Cleanmark home">
          <span className="brand-mark" aria-hidden="true">C</span>
          <span>Cleanmark</span>
        </a>
        <a className="github-link" href="https://github.com/OliverBennettdev/cleanmark">
          GitHub <span aria-hidden="true">↗</span>
        </a>
      </nav>

      <section className="hero" id="top">
        <div className="eyebrow">Privacy hygiene for files you control</div>
        <h1>See what is hidden.<br />Choose what to clean.</h1>
        <p className="hero-copy">
          Inspect invisible text markers and file metadata before making changes. Text can stay entirely in your browser; complex files use a self-hostable cleaner service.
        </p>
        <div className="principles" aria-label="Product principles">
          {principles.map((principle) => (
            <span className="principle" key={principle}><span className="dot" />{principle}</span>
          ))}
        </div>
      </section>

      <CleanerWorkspace />

      <section className="trust-grid" aria-label="How Cleanmark works">
        <article>
          <span className="step-index">01</span>
          <h2>Inspect, don&apos;t guess</h2>
          <p>Cleanmark shows supported findings first. No file is changed just because you selected it.</p>
        </article>
        <article>
          <span className="step-index">02</span>
          <h2>Local where practical</h2>
          <p>Pasted text is inspected and cleaned in your browser by a small, auditable TypeScript package.</p>
        </article>
        <article>
          <span className="step-index">03</span>
          <h2>Self-host the rest</h2>
          <p>PDFs, documents, and image metadata go through an isolated cleaner service you can run yourself.</p>
        </article>
      </section>

      <footer>
        <p>Only process content you own or are authorized to modify.</p>
        <p>Cleanmark does not promise universal watermark detection or removal.</p>
      </footer>
    </main>
  );
}
