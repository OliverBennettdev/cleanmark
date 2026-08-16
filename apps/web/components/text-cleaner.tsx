"use client";

import { cleanText, inspectText, type TextInspection } from "@cleanmark/text-cleaner";
import { useState } from "react";

export function TextCleaner() {
  const [input, setInput] = useState("");
  const [inspection, setInspection] = useState<TextInspection | null>(null);
  const [cleaned, setCleaned] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  function inspect() {
    setInspection(inspectText(input));
    setCleaned(null);
    setCopied(false);
  }

  function clean() {
    const result = cleanText(input);
    setInspection(result.inspection);
    setCleaned(result.text);
    setCopied(false);
  }

  async function copyCleaned() {
    if (cleaned === null) return;
    await navigator.clipboard?.writeText(cleaned);
    setCopied(true);
  }

  const findingCount = inspection?.findings.length ?? 0;

  return (
    <div className="cleaner-panel">
      <div className="panel-heading">
        <div>
          <span className="local-chip">Runs locally</span>
          <h2>Paste text</h2>
          <p>Your text stays in this browser for the default inspect and clean workflow.</p>
        </div>
        <span className="format-hint">Unicode</span>
      </div>

      <label className="field-label" htmlFor="cleanmark-text">Text to inspect</label>
      <textarea
        id="cleanmark-text"
        aria-label="Text to inspect"
        className="text-input"
        placeholder="Paste text here…"
        value={input}
        onChange={(event) => {
          setInput(event.target.value);
          setInspection(null);
          setCleaned(null);
        }}
      />

      <div className="action-row">
        <span className="privacy-note"><span className="lock" aria-hidden="true">◇</span> Nothing uploaded</span>
        <button className="primary-button" disabled={!input} onClick={inspect}>Inspect text</button>
      </div>

      {inspection && (
        <div className="result-card" aria-live="polite">
          <div className="result-heading">
            <div>
              <span className={findingCount ? "status-dot warning" : "status-dot ok"} />
              <strong>{findingCount ? `${findingCount} hidden marker${findingCount === 1 ? "" : "s"} found` : "No supported hidden markers found"}</strong>
            </div>
            <span className="result-caption">Supported Unicode classes only</span>
          </div>

          {findingCount > 0 && (
            <div className="finding-list">
              {inspection.findings.slice(0, 8).map((finding, index) => (
                <div className="finding-row" key={`${finding.index}-${finding.codePoint}-${index}`}>
                  <code>{finding.codePoint}</code>
                  <span>{finding.label}</span>
                  <span className="finding-index">index {finding.index}</span>
                </div>
              ))}
              {findingCount > 8 && <p className="more-findings">+ {findingCount - 8} more findings</p>}
            </div>
          )}

          {findingCount > 0 && cleaned === null && (
            <div className="result-actions"><button className="secondary-button" onClick={clean}>Clean text</button></div>
          )}

          {cleaned !== null && (
            <div className="cleaned-output">
              <label className="field-label" htmlFor="cleaned-text">Cleaned preview</label>
              <textarea id="cleaned-text" className="text-input compact" readOnly value={cleaned} />
              <div className="result-actions">
                <span className="success-note">Cleaned deterministically in your browser.</span>
                <button className="secondary-button" onClick={copyCleaned}>{copied ? "Copied" : "Copy cleaned text"}</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
