from datetime import datetime
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base

class ChannelMember(Base):
    __tablename__ = "channel_members"
    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(foreign_key="channels.id")
    user_id: Mapped[int] = mapped_column(foreign_key="users.id")
    role: Mapped[str] = mapped_column(String(50))
    joined_at: Mapped[datetime] = mapped_column(server_default=func.now())
    