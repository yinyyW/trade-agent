from __future__ import annotations

import re


class SemanticTextSplitter:
    """
    Lightweight Chinese-friendly splitter.

    It first splits by headings/paragraphs and then enforces a maximum
    character window. For MVP this avoids introducing a tokenizer dependency.
    """

    def __init__(self, chunk_size: int = 600, overlap: int = 100):
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text: str) -> list[str]:
        text = re.sub(r"\r\n?", "\n", text).strip()
        if not text:
            return []

        paragraphs = [
            p.strip()
            for p in re.split(r"\n{2,}", text)
            if p.strip()
        ]

        chunks: list[str] = []
        current = ""

        for paragraph in paragraphs:
            if len(paragraph) > self.chunk_size:
                if current:
                    chunks.append(current)
                    current = ""

                chunks.extend(self._split_long(paragraph))
                continue

            candidate = paragraph if not current else current + "\n\n" + paragraph
            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                chunks.append(current)
                tail = current[-self.overlap:]
                current = tail + "\n\n" + paragraph

        if current:
            chunks.append(current)

        return [x.strip() for x in chunks if x.strip()]

    def _split_long(self, text: str) -> list[str]:
        result = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))

            if end < len(text):
                boundary = max(
                    text.rfind("。", start, end),
                    text.rfind("；", start, end),
                    text.rfind("，", start, end),
                    text.rfind("\n", start, end),
                )
                if boundary > start + self.chunk_size // 2:
                    end = boundary + 1

            result.append(text[start:end].strip())
            if end >= len(text):
                break

            start = max(end - self.overlap, start + 1)

        return result
