from datetime import datetime
from pydantic import BaseModel


class MessageCreate(BaseModel):
    channel_id: int
    content: str
    client_message_id: str


class MessageResponse(BaseModel):
    id: int
    channel_id: int
    sender_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageHistoryResponse(BaseModel):
    messages: list[MessageResponse]
    next_cursor: int | None