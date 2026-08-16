from cleaner.classify import classify_bytes


def test_classifies_png():
    assert classify_bytes(b"\x89PNG\r\n\x1a\nrest", "image.png") == "image"


def test_classifies_jpeg():
    assert classify_bytes(b"\xff\xd8\xffrest", "photo.jpg") == "image"


def test_classifies_webp():
    assert classify_bytes(b"RIFF\x00\x00\x00\x00WEBPrest", "photo.webp") == "image"


def test_classifies_pdf():
    assert classify_bytes(b"%PDF-1.7\n", "report.pdf") == "container"


def test_classifies_docx_zip_by_extension_and_magic():
    assert classify_bytes(b"PK\x03\x04rest", "report.docx") == "container"


def test_classifies_text_and_markdown():
    assert classify_bytes("你好\nhello".encode(), "notes.md") == "text"
    assert classify_bytes(b"plain text", "notes.txt") == "text"


def test_unknown_binary_is_unsupported():
    assert classify_bytes(b"\x00\x01\x02\x03\x04\x05" * 30, "blob.bin") == "unsupported"
