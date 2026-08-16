export type FindingCategory =
  | "zero-width"
  | "soft-hyphen"
  | "bidi-control"
  | "tag"
  | "unusual-space";

export type TextFinding = {
  codePoint: string;
  char: string;
  index: number;
  category: FindingCategory;
  label: string;
};

export type TextInspection = {
  suspicious: boolean;
  findings: TextFinding[];
  counts: Record<FindingCategory, number>;
};

export type CleanTextResult = {
  text: string;
  inspection: TextInspection;
  removed: number;
};

const LABELS = new Map<number, string>([
  [0x00ad, "Soft Hyphen"], [0x061c, "Arabic Letter Mark"], [0x200b, "Zero Width Space"],
  [0x200c, "Zero Width Non-Joiner"], [0x200d, "Zero Width Joiner"], [0x200e, "Left-to-Right Mark"],
  [0x200f, "Right-to-Left Mark"], [0x202a, "Left-to-Right Embedding"], [0x202b, "Right-to-Left Embedding"],
  [0x202c, "Pop Directional Formatting"], [0x202d, "Left-to-Right Override"], [0x202e, "Right-to-Left Override"],
  [0x2060, "Word Joiner"], [0x2066, "Left-to-Right Isolate"], [0x2067, "Right-to-Left Isolate"],
  [0x2068, "First Strong Isolate"], [0x2069, "Pop Directional Isolate"], [0xfeff, "Zero Width No-Break Space"],
  [0xe0001, "Language Tag"],
]);

const UNUSUAL_SPACES = new Set([0x00a0, 0x1680, 0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005, 0x2006, 0x2007, 0x2008, 0x2009, 0x200a, 0x202f, 0x205f, 0x3000]);

function classify(codePoint: number): FindingCategory | null {
  if (codePoint === 0x00ad) return "soft-hyphen";
  if (codePoint === 0x200b || codePoint === 0x200c || codePoint === 0x200d || codePoint === 0x2060 || codePoint === 0xfeff) return "zero-width";
  if (codePoint === 0x061c || codePoint === 0x200e || codePoint === 0x200f || (codePoint >= 0x202a && codePoint <= 0x202e) || (codePoint >= 0x2066 && codePoint <= 0x2069)) return "bidi-control";
  if (codePoint === 0xe0001 || (codePoint >= 0xe0020 && codePoint <= 0xe007f)) return "tag";
  if (UNUSUAL_SPACES.has(codePoint)) return "unusual-space";
  return null;
}

function codePointLabel(codePoint: number, category: FindingCategory): string {
  if (LABELS.has(codePoint)) return LABELS.get(codePoint)!;
  if (category === "tag") return "Unicode Tag Character";
  if (category === "unusual-space") return "Unusual Space";
  return "Hidden Unicode Character";
}

function formatCodePoint(codePoint: number): string { return `U+${codePoint.toString(16).toUpperCase().padStart(4, "0")}`; }

export function inspectText(input: string): TextInspection {
  const findings: TextFinding[] = [];
  const counts: Record<FindingCategory, number> = { "zero-width": 0, "soft-hyphen": 0, "bidi-control": 0, tag: 0, "unusual-space": 0 };
  let index = 0;
  for (const char of input) {
    const codePoint = char.codePointAt(0)!;
    const category = classify(codePoint);
    if (category) {
      findings.push({ codePoint: formatCodePoint(codePoint), char, index, category, label: codePointLabel(codePoint, category) });
      counts[category] += 1;
    }
    index += char.length;
  }
  return { suspicious: findings.length > 0, findings, counts };
}

export function cleanText(input: string): CleanTextResult {
  const inspection = inspectText(input);
  let text = "";
  let removed = 0;
  for (const char of input) {
    const category = classify(char.codePointAt(0)!);
    if (category === "unusual-space") text += " ";
    else if (category) removed += 1;
    else text += char;
  }
  return { text, inspection, removed };
}
