from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agent.service import AgentService


router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


class ChatRequest(BaseModel):

    conversation_id: str

    message: str

    agent_type: str = "general"


@router.post(
    "/stream"
)
async def chat_stream(
    request: ChatRequest,
    agent_service: AgentService = Depends(
        get_agent_service
    ),
):

    async def event_generator():

        from langchain_core.messages import HumanMessage

        messages = [
            HumanMessage(
                content=request.message
            )
        ]

        try:

            yield (
                "event: message_start\n"
                "data: {}\n\n"
            )

            async for event in agent_service.stream(
                agent_type=request.agent_type,
                messages=messages,
                conversation_id=request.conversation_id,
            ):

                payload = json.dumps(
                    event.to_dict(),
                    ensure_ascii=False,
                )

                yield (
                    f"data: {payload}\n\n"
                )

        except Exception as exc:

            payload = json.dumps(
                {
                    "type": "error",
                    "data": {
                        "message": str(exc),
                    },
                },
                ensure_ascii=False,
            )

            yield (
                f"event: error\n"
                f"data: {payload}\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )