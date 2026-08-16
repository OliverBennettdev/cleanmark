"use client";

import { useEffect, useRef, useState } from "react";

const MAX_BYTES = 25 * 1024 * 1024;

type InspectPayload = {
  ok: boolean;
  kind: string;
  suspicious: boolean;
  report: Record<string, unknown>;
};

type State = "idle" | "inspecting" | "inspected" | "cleaning" | "cleaned" | "error";

function humanSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function errorMessage(code?: string) {
  switch (code) {
    case "too-large": return "That file is larger than the 25 MiB limit.";
    case "unsupported": return "That file format is not supported in Cleanmark v0.1.";
    case "malformed": return "The file could not be read safely.";
    case "capability-unavailable": return "This cleaner instance is missing a tool required for that file type.";
    default: return "Cleanmark could not complete that operation.";
  }
}

export function FileCleaner() {
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<State>("idle");
  const [inspection, setInspection] = useState<InspectPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [download, setDownload] = useState<{ url: string; name: string } | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => () => {
    if (download?.url.startsWith("blob:")) URL.revokeObjectURL(download.url);
  }, [download]);

  function chooseFile(next: File | null) {
    if (download?.url.startsWith("blob:")) URL.revokeObjectURL(download.url);
    setDownload(null);
    setInspection(null);
    setError(null);
    setFile(next);
    setState("idle");
    if (next && next.size > MAX_BYTES) {
      setError(errorMessage("too-large"));
      setState("error");
    }
  }

  async function inspect() {
    if (!file || file.size > MAX_BYTES) return;
    setState("inspecting");
    setError(null);
    const form = new FormData();
    form.append("file", file);
    try {
      const response = await fetch("/api/inspect", { method: "POST", body: form });
      const payload = await response.json();
      if (!response.ok) throw new Error(errorMessage(payload?.error?.code));
      setInspection(payload);
      setState("inspected");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : errorMessage());
      setState("error");
    }
  }

  async function clean() {
    if (!file || !inspection) return;
    setState("cleaning");
    setError(null);
    const form = new FormData();
    form.append("file", file);
    try {
      const response = await fetch("/api/clean", { method: "POST", body: form });
      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        throw new Error(errorMessage(payload?.error?.code));
      }
      const blob = await response.blob();
      const disposition = response.headers.get("Content-Disposition") ?? "";
      const match = /filename="([^"]+)"/.exec(disposition);
      const name = match?.[1] ?? `cleaned-${file.name}`;
      const url = typeof URL.createObjectURL === "function" ? URL.createObjectURL(blob) : "#";
      setDownload({ url, name });
      setState("cleaned");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : errorMessage());
      setState("error");
    }
  }

  return (
    <div className="cleaner-panel">
      <div className="panel-heading">
        <div>
          <span className="server-chip">Ephemeral server processing</span>
          <h2>Upload a file</h2>
          <p>Inspect first. Cleaning only starts after you explicitly request it.</p>
        </div>
        <span className="format-hint">25 MiB max</span>
      </div>

      <input
        ref={inputRef}
        className="visually-hidden"
        type="file"
        aria-label="Choose a file"
        accept=".png,.jpg,.jpeg,.webp,.pdf,.docx,.txt,.md,.markdown"
        onChange={(event) => chooseFile(event.target.files?.[0] ?? null)}
      />

      <button className={`drop-zone ${file ? "has-file" : ""}`} onClick={() => inputRef.current?.click()} type="button">
        <span className="upload-glyph" aria-hidden="true">↑</span>
        {file ? (
          <span className="file-summary"><strong>{file.name}</strong><small>{humanSize(file.size)}</small></span>
        ) : (
          <span><strong>Choose a file</strong><small>PNG · JPEG · WebP · PDF · DOCX · TXT · MD</small></span>
        )}
      </button>

      <div className="action-row">
        <span className="privacy-note">Uploads are temporary by default</span>
        <button className="primary-button" disabled={!file || state === "inspecting" || state === "cleaning" || file.size > MAX_BYTES} onClick={inspect}>
          {state === "inspecting" ? "Inspecting…" : "Inspect file"}
        </button>
      </div>

      {error && <div className="error-card" role="alert">{error}</div>}

      {inspection && state !== "error" && (
        <div className="result-card" aria-live="polite">
          <div className="result-heading">
            <div>
              <span className={inspection.suspicious ? "status-dot warning" : "status-dot ok"} />
              <strong>{inspection.suspicious ? "Findings detected" : "No supported findings detected"}</strong>
            </div>
            <span className="result-caption">{inspection.kind}</span>
          </div>
          <details className="report-details">
            <summary>View inspection report</summary>
            <pre>{JSON.stringify(inspection.report, null, 2)}</pre>
          </details>
          {state === "inspected" && (
            <div className="result-actions">
              <span className="success-note">Your original file has not been changed.</span>
              <button className="secondary-button" onClick={clean}>Clean file</button>
            </div>
          )}
          {state === "cleaning" && <p className="working-note">Creating a cleaned copy…</p>}
          {state === "cleaned" && download && (
            <div className="result-actions">
              <span className="success-note">Your cleaned copy is ready.</span>
              <a className="secondary-button link-button" href={download.url} download={download.name}>Download cleaned file</a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
