import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { FileCleaner } from "./file-cleaner";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("FileCleaner", () => {
  it("requires inspection before an explicit clean", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn()
        .mockResolvedValueOnce(
          new Response(JSON.stringify({ ok: true, kind: "text", suspicious: true, report: { findings: [{ code_point: "U+200B" }] } }), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          }),
        )
        .mockResolvedValueOnce(
          new Response(new Blob(["helloworld"]), {
            status: 200,
            headers: { "Content-Disposition": 'attachment; filename="notes.cleaned.txt"' },
          }),
        ),
    );

    render(<FileCleaner />);
    const file = new File(["hello\u200bworld"], "notes.txt", { type: "text/plain" });
    fireEvent.change(screen.getByLabelText("Choose a file"), { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: "Inspect file" }));

    await screen.findByText(/findings detected/i);
    expect(screen.getByRole("button", { name: "Clean file" })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Clean file" }));
    await waitFor(() => expect(screen.getByText(/cleaned copy is ready/i)).toBeInTheDocument());
  });
});
