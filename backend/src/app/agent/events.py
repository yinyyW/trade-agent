from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AgentEvent:

    type: str

    data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:

        return {
            "type": self.type,
            "data": self.data,
        }