import pytest

from app.rag.splitter import SemanticTextSplitter


def test_empty_text_returns_empty_list():
    splitter = SemanticTextSplitter()
    assert splitter.split("") == []
    assert splitter.split("   \n\n ") == []


def test_normalizes_crlf_and_splits_paragraphs():
    splitter = SemanticTextSplitter(chunk_size=50, overlap=5)
    text = "第一段。\r\n\r\n第二段。\r\n\r\n第三段。"
    chunks = splitter.split(text)
    assert chunks
    assert "\r" not in "".join(chunks)
    assert "第一段。" in chunks[0]


def test_chunk_never_exceeds_configured_size_for_long_text():
    splitter = SemanticTextSplitter(chunk_size=30, overlap=5)
    text = "这是一个用于测试长文本切分的句子。" * 20
    chunks = splitter.split(text)
    assert len(chunks) > 1
    assert all(len(chunk) <= 30 for chunk in chunks)


def test_overlap_preserves_context_between_long_chunks():
    splitter = SemanticTextSplitter(chunk_size=20, overlap=5)
    text = "abcdefghijklmnopqrstuvwx"
    chunks = splitter.split(text)
    assert len(chunks) >= 2
    assert chunks[0][-5:] == chunks[1][:5]


def test_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ValueError):
        SemanticTextSplitter(chunk_size=100, overlap=100)


def test_punctuation_is_preferred_as_split_boundary():
    splitter = SemanticTextSplitter(chunk_size=18, overlap=3)
    text = "第一句用于测试切分。第二句也用于测试切分。第三句。"
    chunks = splitter.split(text)
    assert len(chunks) >= 2
    assert all(len(chunk) <= 18 for chunk in chunks)
    assert any("。" in chunk for chunk in chunks[:-1])
