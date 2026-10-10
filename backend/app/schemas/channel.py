from datetime import datetime
from pydantic import BaseModel

class ChannelCreate(BaseModel):
    name: str


class ChannelResponse(BaseModel):
    id: int
    name: str
    is_dm: bool
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True


class ChannelMemberResponse(BaseModel):

    role: str
    user_id: int
    joined_at: datetime

    class Config:
        from_attributes = True


class DMCreate(BaseModel):
    user_id: int