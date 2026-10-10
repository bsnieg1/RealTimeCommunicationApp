from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.channel_member import ChannelMember
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate, MessageHistoryResponse, MessageResponse

router = APIRouter(prefix="/messages", tags=["messages"])


async def _require_membership(channel_id: int, user_id: int, db: AsyncSession) -> None:
    member = await db.scalar(
        select(ChannelMember).where(
            ChannelMember.channel_id == channel_id, ChannelMember.user_id == user_id
        )
    )
    if member is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this channel")


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    body: MessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Message:
    await _require_membership(body.channel_id, user.id, db)

    existing = await db.scalar(
        select(Message).where(
            Message.sender_id == user.id, Message.client_message_id == body.client_message_id
        )
    )
    if existing is not None:
        return existing  # retry of the same send — idempotent, not an error

    message = Message(
        channel_id=body.channel_id,
        sender_id=user.id,
        content=body.content,
        client_message_id=body.client_message_id,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


@router.get("", response_model=MessageHistoryResponse)
async def get_history(
    channel_id: int,
    cursor: int | None = None,
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageHistoryResponse:
    await _require_membership(channel_id, user.id, db)

    query = select(Message).where(Message.channel_id == channel_id)
    if cursor is not None:
        query = query.where(Message.id < cursor)
    query = query.order_by(Message.id.desc()).limit(limit)

    result = await db.scalars(query)
    messages = list(result)

    next_cursor = messages[-1].id if len(messages) == limit else None
    return MessageHistoryResponse(messages=messages, next_cursor=next_cursor)
