from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypedDict

MessageRole = Literal["system", "user", "assistant"]


class MessageDict(TypedDict):
    role: MessageRole
    content: str


@dataclass
class Message:
    """OpenAI Message object containing a role and the message content"""

    role: MessageRole
    content: str

    def __init__(self, role: MessageRole, content: str):
        self.role = role
        self.content = content

    def raw(self) -> MessageDict:
        return {"role": self.role, "content": self.content}
    
    @classmethod
    def from_json(cls, json_dict: dict):
        return cls(role=json_dict["role"], content=json_dict["content"])


@dataclass
class ChatSequence:
    """Utility container for a chat sequence"""

    messages: list[Message] = field(default_factory=list)

    def __getitem__(self, i: int):
        return self.messages[i]

    def append(self, message: Message):
        return self.messages.append(message)

    def raw(self) -> list[dict]:
        return [message.raw() for message in self.messages]
    
    def pop(self, i: int = -1):
        return self.messages.pop(i)
    
    @classmethod
    def from_json(cls, json_list: list[dict]):
        return cls(messages=[Message.from_json(json_dict) for json_dict in json_list])
