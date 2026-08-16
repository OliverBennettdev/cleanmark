"use client";

import { useState } from "react";

import { FileCleaner } from "./file-cleaner";
import { TextCleaner } from "./text-cleaner";

type Mode = "text" | "file";

export function CleanerWorkspace() {
  const [mode, setMode] = useState<Mode>("text");

  return (
    <section className="workspace" aria-label="Cleanmark cleaner">
      <div className="mode-tabs" role="tablist" aria-label="Cleaner mode">
        <button className={mode === "text" ? "active" : ""} role="tab" aria-selected={mode === "text"} onClick={() => setMode("text")}>Paste text</button>
        <button className={mode === "file" ? "active" : ""} role="tab" aria-selected={mode === "file"} onClick={() => setMode("file")}>Upload file</button>
      </div>
      <div className="workspace-body">{mode === "text" ? <TextCleaner /> : <FileCleaner />}</div>
    </section>
  );
}
