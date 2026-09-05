from __future__ import annotations

from typing import Any


def format_rag_context(
    contexts: list[dict[str, Any]],
) -> str:

    if not contexts:
        return "没有检索到相关知识库内容。"

    blocks: list[str] = []

    for index, item in enumerate(contexts, start=1):

        title = item.get("title", "")
        content = item.get("content", "")
        score = item.get("score", 0)

        blocks.append(
            f"""
            [知识片段 {index}]
            标题：{title}
            相关度：{score:.4f}

            {content}
            """.strip()
        )

    return "\n\n".join(blocks)