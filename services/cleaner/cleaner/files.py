from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from .classify import classify_bytes
from .text import clean_text, inspect_text


class UnsupportedFormat(ValueError):
    pass


class CapabilityUnavailable(RuntimeError):
    pass


def capabilities() -> dict[str, bool]:
    return {
        "exiftool": shutil.which("exiftool") is not None,
        "qpdf": shutil.which("qpdf") is not None,
        "c2patool": shutil.which("c2patool") is not None,
    }


def _run_json(command: list[str]) -> Any:
    completed = subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
    return json.loads(completed.stdout)


def _inspect_with_exiftool(path: Path) -> dict[str, Any]:
    if not shutil.which("exiftool"):
        return {"available": False, "metadata": {}}
    payload = _run_json(["exiftool", "-json", "-G1", "-a", str(path)])
    row = payload[0] if isinstance(payload, list) and payload else {}
    metadata = {key: value for key, value in row.items() if not key.endswith(":SourceFile")}
    return {"available": True, "metadata": metadata}


def _inspect_c2pa(path: Path) -> dict[str, Any]:
    if not shutil.which("c2patool"):
        return {"available": False, "present": None}
    completed = subprocess.run(
        ["c2patool", str(path), "--json"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    text = completed.stdout.strip()
    present = completed.returncode == 0 and bool(text) and text not in {"{}", "[]"}
    return {"available": True, "present": present}


def _inspect_docx(data: bytes) -> dict[str, Any]:
    metadata_parts: list[str] = []
    hidden_findings = 0
    with tempfile.TemporaryDirectory(prefix="cleanmark-docx-inspect-") as tmp:
        path = Path(tmp) / "input.docx"
        path.write_bytes(data)
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                if info.filename.startswith("docProps/"):
                    metadata_parts.append(info.filename)
                if info.filename.startswith("word/") and info.filename.endswith(".xml"):
                    try:
                        text = archive.read(info).decode("utf-8")
                    except UnicodeDecodeError:
                        continue
                    hidden_findings += len(inspect_text(text)["findings"])
    return {
        "metadata_parts": sorted(metadata_parts),
        "hidden_text_findings": hidden_findings,
    }


def inspect_file(data: bytes, filename: str) -> tuple[str, dict[str, Any], bool]:
    kind = classify_bytes(data, filename)
    if kind == "unsupported":
        raise UnsupportedFormat("unsupported file format")
    if kind == "text":
        text = data.decode("utf-8")
        report = inspect_text(text)
        return kind, report, bool(report["suspicious"])
    if filename.lower().endswith(".docx"):
        report = _inspect_docx(data)
        suspicious = bool(report["metadata_parts"] or report["hidden_text_findings"])
        return kind, report, suspicious

    with tempfile.TemporaryDirectory(prefix="cleanmark-inspect-") as tmp:
        path = Path(tmp) / Path(filename).name
        path.write_bytes(data)
        exif = _inspect_with_exiftool(path)
        c2pa = _inspect_c2pa(path)
    report = {"exif": exif, "c2pa": c2pa}
    suspicious = bool(exif.get("metadata")) or c2pa.get("present") is True
    return kind, report, suspicious


def _strip_docprops_references(filename: str, payload: bytes) -> bytes:
    if filename not in {"[Content_Types].xml", "_rels/.rels"}:
        return payload
    try:
        root = ET.fromstring(payload)
    except ET.ParseError:
        return payload
    changed = False
    for child in list(root):
        part_name = child.attrib.get("PartName", "")
        target = child.attrib.get("Target", "")
        if part_name.startswith("/docProps/") or target.startswith("docProps/"):
            root.remove(child)
            changed = True
    if not changed:
        return payload
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _clean_docx(data: bytes) -> tuple[bytes, dict[str, Any]]:
    removed_parts: list[str] = []
    cleaned_xml_parts = 0
    total_removed = 0
    total_normalized = 0
    with tempfile.TemporaryDirectory(prefix="cleanmark-docx-clean-") as tmp:
        src = Path(tmp) / "input.docx"
        dst = Path(tmp) / "output.docx"
        src.write_bytes(data)
        with zipfile.ZipFile(src, "r") as source, zipfile.ZipFile(dst, "w") as target:
            for info in source.infolist():
                if info.filename.startswith("docProps/"):
                    removed_parts.append(info.filename)
                    continue
                payload = source.read(info)
                payload = _strip_docprops_references(info.filename, payload)
                if info.filename.startswith("word/") and info.filename.endswith(".xml"):
                    try:
                        decoded = payload.decode("utf-8")
                    except UnicodeDecodeError:
                        pass
                    else:
                        cleaned, stats = clean_text(decoded)
                        if cleaned != decoded:
                            cleaned_xml_parts += 1
                            total_removed += int(stats["removed"])
                            total_normalized += int(stats["normalized_spaces"])
                            payload = cleaned.encode("utf-8")
                target.writestr(info, payload)
        output = dst.read_bytes()
    return output, {
        "removed_metadata_parts": sorted(removed_parts),
        "cleaned_xml_parts": cleaned_xml_parts,
        "removed": total_removed,
        "normalized_spaces": total_normalized,
    }


def _clean_external(data: bytes, filename: str) -> tuple[bytes, dict[str, Any]]:
    suffix = Path(filename).suffix.lower()
    tools = capabilities()
    with tempfile.TemporaryDirectory(prefix="cleanmark-file-clean-") as tmp:
        src = Path(tmp) / f"input{suffix}"
        dst = Path(tmp) / f"output{suffix}"
        src.write_bytes(data)

        if suffix == ".pdf":
            if not tools["qpdf"]:
                raise CapabilityUnavailable("qpdf is required to clean PDF files")
            subprocess.run(
                ["qpdf", "--object-streams=generate", str(src), str(dst)],
                check=True,
                capture_output=True,
                timeout=60,
            )
        else:
            shutil.copyfile(src, dst)

        if not tools["exiftool"]:
            raise CapabilityUnavailable("exiftool is required to clean image/PDF metadata")
        subprocess.run(
            ["exiftool", "-all=", "-overwrite_original", str(dst)],
            check=True,
            capture_output=True,
            timeout=60,
        )
        return dst.read_bytes(), {"metadata_stripped": True, "tools": tools}


def clean_file(data: bytes, filename: str) -> tuple[str, bytes, dict[str, Any]]:
    kind = classify_bytes(data, filename)
    if kind == "unsupported":
        raise UnsupportedFormat("unsupported file format")
    if kind == "text":
        cleaned, stats = clean_text(data.decode("utf-8"))
        return kind, cleaned.encode("utf-8"), stats
    if filename.lower().endswith(".docx"):
        cleaned, report = _clean_docx(data)
        return kind, cleaned, report
    cleaned, report = _clean_external(data, filename)
    return kind, cleaned, report
