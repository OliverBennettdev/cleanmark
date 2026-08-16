from __future__ import annotations

from dataclasses import dataclass, asdict

_CATEGORIES = ("zero-width", "soft-hyphen", "bidi-control", "tag", "unusual-space")
_UNUSUAL_SPACES = {
    0x00A0,
    0x1680,
    *range(0x2000, 0x200B),
    0x202F,
    0x205F,
    0x3000,
}
_LABELS = {
    0x00AD: "Soft Hyphen",
    0x061C: "Arabic Letter Mark",
    0x200B: "Zero Width Space",
    0x200C: "Zero Width Non-Joiner",
    0x200D: "Zero Width Joiner",
    0x200E: "Left-to-Right Mark",
    0x200F: "Right-to-Left Mark",
    0x202A: "Left-to-Right Embedding",
    0x202B: "Right-to-Left Embedding",
    0x202C: "Pop Directional Formatting",
    0x202D: "Left-to-Right Override",
    0x202E: "Right-to-Left Override",
    0x2060: "Word Joiner",
    0x2066: "Left-to-Right Isolate",
    0x2067: "Right-to-Left Isolate",
    0x2068: "First Strong Isolate",
    0x2069: "Pop Directional Isolate",
    0xFEFF: "Zero Width No-Break Space",
    0xE0001: "Language Tag",
}


@dataclass(frozen=True)
class Finding:
    code_point: str
    char: str
    index: int
    category: str
    label: str


def _category(code_point: int) -> str | None:
    if code_point == 0x00AD:
        return "soft-hyphen"
    if code_point in {0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF}:
        return "zero-width"
    if (
        code_point in {0x061C, 0x200E, 0x200F}
        or 0x202A <= code_point <= 0x202E
        or 0x2066 <= code_point <= 0x2069
    ):
        return "bidi-control"
    if code_point == 0xE0001 or 0xE0020 <= code_point <= 0xE007F:
        return "tag"
    if code_point in _UNUSUAL_SPACES:
        return "unusual-space"
    return None


def _label(code_point: int, category: str) -> str:
    if code_point in _LABELS:
        return _LABELS[code_point]
    if category == "tag":
        return "Unicode Tag Character"
    if category == "unusual-space":
        return "Unusual Space"
    return "Hidden Unicode Character"


def inspect_text(text: str) -> dict[str, object]:
    findings: list[Finding] = []
    counts = {category: 0 for category in _CATEGORIES}
    utf16_index = 0
    for char in text:
        cp = ord(char)
        category = _category(cp)
        if category:
            findings.append(
                Finding(
                    code_point=f"U+{cp:04X}",
                    char=char,
                    index=utf16_index,
                    category=category,
                    label=_label(cp, category),
                )
            )
            counts[category] += 1
        utf16_index += 2 if cp > 0xFFFF else 1
    return {
        "suspicious": bool(findings),
        "findings": [asdict(item) for item in findings],
        "counts": counts,
    }


def clean_text(text: str) -> tuple[str, dict[str, object]]:
    inspection = inspect_text(text)
    output: list[str] = []
    removed = 0
    normalized_spaces = 0
    for char in text:
        category = _category(ord(char))
        if category == "unusual-space":
            output.append(" ")
            normalized_spaces += 1
        elif category:
            removed += 1
        else:
            output.append(char)
    return "".join(output), {
        "removed": removed,
        "normalized_spaces": normalized_spaces,
        "inspection": inspection,
    }
