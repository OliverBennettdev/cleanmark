import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { TextCleaner } from "./text-cleaner";

describe("TextCleaner", () => {
  it("inspects before cleaning and keeps text local", () => {
    render(<TextCleaner />);
    fireEvent.change(screen.getByLabelText("Text to inspect"), {
      target: { value: "hello\u200bworld" },
    });

    fireEvent.click(screen.getByRole("button", { name: "Inspect text" }));
    expect(screen.getByText(/1 hidden marker found/i)).toBeInTheDocument();
    expect(screen.getByText(/stays in this browser/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Clean text" }));
    expect(screen.getByDisplayValue("helloworld")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Copy cleaned text" })).toBeInTheDocument();
  });
});
