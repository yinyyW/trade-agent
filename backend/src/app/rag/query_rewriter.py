from __future__ import annotations

from abc import ABC, abstractmethod


class QueryRewriter(ABC):
    @abstractmethod
    async def rewrite(self, query: str) -> str:
        raise NotImplementedError


class IdentityQueryRewriter(QueryRewriter):
    async def rewrite(self, query: str) -> str:
        return query.strip()


class DeepSeekQueryRewriter(QueryRewriter):
    def __init__(self, api_key: str, base_url: str, model: str):
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def rewrite(self, query: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是金融知识库检索查询改写器。"
                        "将用户问题改写成适合金融知识库语义检索的短查询。"
                        "保留股票、指标、政策、财报等关键实体。"
                        "不要补造实时行情数据，不要回答问题，只输出检索查询。"
                    ),
                },
                {"role": "user", "content": query},
            ],
        )
        return (response.choices[0].message.content or query).strip()
