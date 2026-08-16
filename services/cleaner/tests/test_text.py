from cleaner.text import clean_text, inspect_text


def test_zero_width_space_is_found_and_removed():
    report = inspect_text("hello\u200bworld")
    assert report["findings"][0] == {
        "code_point": "U+200B",
        "char": "\u200b",
        "index": 5,
        "category": "zero-width",
        "label": "Zero Width Space",
    }
    cleaned, stats = clean_text("hello\u200bworld")
    assert cleaned == "helloworld"
    assert stats["removed"] == 1


def test_unusual_spaces_are_normalized():
    cleaned, stats = clean_text("hello\u00a0world\u2009again")
    assert cleaned == "hello world again"
    assert stats["normalized_spaces"] == 2


def test_bidi_and_tag_chars_are_removed():
    input_text = "abc\u202edef" + chr(0xE0001)
    cleaned, stats = clean_text(input_text)
    assert cleaned == "abcdef"
    assert stats["removed"] == 2


def test_normal_multilingual_text_is_preserved():
    text = "你好，世界 — مرحبًا — hello"
    cleaned, stats = clean_text(text)
    assert cleaned == text
    assert stats["removed"] == 0
    assert inspect_text(text)["suspicious"] is False
