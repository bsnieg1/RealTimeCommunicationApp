from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.channel import Channel
from app.models.channel_member import ChannelMember
from app.models.user import User
from app.schemas.channel import ChannelCreate, ChannelMemberResponse, ChannelResponse, DMCreate

router = APIRouter(prefix="/channels", tags=["channels"])


@router.post("", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    body: ChannelCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    ) -> Channel:
    channel = Channel(name=body.name, created_by=user.id, is_dm=False)
    db.add(channel)
    await db.flush()  # assigns channel.id without a full commit yet

    db.add(ChannelMember(channel_id=channel.id, user_id=user.id, role="owner"))
    await db.commit()
    await db.refresh(channel)
    return channel


@router.get("", response_model=list[ChannelResponse])
async def list_my_channels(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Channel]:
    result = await db.scalars(
        select(Channel).join(ChannelMember).where(ChannelMember.user_id == user.id)
    )
    return list(result)


@router.post("/{channel_id}/join", status_code=status.HTTP_204_NO_CONTENT)
async def join_channel(
    channel_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    channel = await db.get(Channel, channel_id)
    if channel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")

    existing = await db.scalar(
        select(ChannelMember).where(
            ChannelMember.channel_id == channel_id, ChannelMember.user_id == user.id
        )
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already a member")

    db.add(ChannelMember(channel_id=channel_id, user_id=user.id, role="member"))
    await db.commit()


@router.get("/{channel_id}/members", response_model=list[ChannelMemberResponse])
async def list_members(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[ChannelMember]:
    result = await db.scalars(select(ChannelMember).where(ChannelMember.channel_id == channel_id))
    return list(result)


@router.post("/dm", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_or_get_dm(
    body: DMCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Channel:
    if body.user_id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot DM yourself")

    other = await db.get(User, body.user_id)
    if other is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    a_id, b_id = sorted((user.id, body.user_id))
    existing = await db.scalar(
        select(Channel).where(Channel.is_dm.is_(True), Channel.name == f"dm-{a_id}-{b_id}")
    )
    if existing is not None:
        return existing

    channel = Channel(name=f"dm-{a_id}-{b_id}", created_by=user.id, is_dm=True)
    db.add(channel)
    await db.flush()

    db.add(ChannelMember(channel_id=channel.id, user_id=a_id, role="member"))
    db.add(ChannelMember(channel_id=channel.id, user_id=b_id, role="member"))
    await db.commit()
    await db.refresh(channel)
    return channel
