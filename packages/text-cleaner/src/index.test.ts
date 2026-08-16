import assert from "node:assert/strict";
import test from "node:test";
import { cleanText, inspectText } from "./index.ts";

test("finds and removes zero-width space", () => {
  const input = "hello\u200bworld";
  assert.deepEqual(inspectText(input).findings[0], { codePoint: "U+200B", char: "\u200b", index: 5, category: "zero-width", label: "Zero Width Space" });
  assert.equal(cleanText(input).text, "helloworld");
});
test("finds and removes soft hyphen", () => { const result = cleanText("co\u00adoperate"); assert.equal(result.text, "cooperate"); assert.equal(result.removed, 1); });
test("finds and removes bidi controls", () => { assert.equal(inspectText("abc\u202edef").findings[0]?.category, "bidi-control"); assert.equal(cleanText("abc\u202edef").text, "abcdef"); });
test("finds and removes tag characters", () => { const input = `hello${String.fromCodePoint(0xe0001)}world`; assert.equal(inspectText(input).findings[0]?.codePoint, "U+E0001"); assert.equal(cleanText(input).text, "helloworld"); });
test("normalizes unusual spaces to ASCII space", () => { const result = cleanText("hello\u00a0world\u2009again"); assert.equal(result.text, "hello world again"); assert.equal(result.removed, 0); assert.equal(result.inspection.counts["unusual-space"], 2); });
test("preserves ordinary multilingual text", () => { const input = "你好，世界 — مرحبًا — hello"; assert.equal(cleanText(input).text, input); assert.equal(inspectText(input).suspicious, false); });
test("reports UTF-16 string indexes deterministically", () => { const input = `😀a\u200bb`; assert.equal(inspectText(input).findings[0]?.index, 3); });
