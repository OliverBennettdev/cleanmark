from __future__ import annotations

import io
import zipfile

from cleaner.files import clean_file, inspect_file


def _docx_fixture() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
            "</Types>",
        )
        archive.writestr(
            "_rels/.rels",
            '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Target="word/document.xml" Type="officeDocument"/>'
            '<Relationship Id="rId2" Target="docProps/core.xml" Type="metadata/core-properties"/>'
            "</Relationships>",
        )
        archive.writestr("docProps/core.xml", "<cp:coreProperties xmlns:cp=\"urn:test\"><cp:title>Secret</cp:title></cp:coreProperties>")
        archive.writestr("word/document.xml", "<w:document xmlns:w=\"urn:test\"><w:t>hello\u200bworld</w:t></w:document>")
    return buffer.getvalue()


def test_docx_inspect_finds_metadata_and_hidden_text():
    kind, report, suspicious = inspect_file(_docx_fixture(), "report.docx")
    assert kind == "container"
    assert suspicious is True
    assert report["metadata_parts"] == ["docProps/core.xml"]
    assert report["hidden_text_findings"] == 1


def test_docx_clean_removes_metadata_relationships_and_hidden_text():
    kind, cleaned, report = clean_file(_docx_fixture(), "report.docx")
    assert kind == "container"
    assert report["removed_metadata_parts"] == ["docProps/core.xml"]
    with zipfile.ZipFile(io.BytesIO(cleaned)) as archive:
        assert "docProps/core.xml" not in archive.namelist()
        assert "docProps" not in archive.read("[Content_Types].xml").decode()
        assert "docProps" not in archive.read("_rels/.rels").decode()
        assert "hello\u200bworld" not in archive.read("word/document.xml").decode()
        assert "helloworld" in archive.read("word/document.xml").decode()
