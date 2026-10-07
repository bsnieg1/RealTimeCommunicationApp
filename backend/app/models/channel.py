from datatime import datetime
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base

class Channel(Base):
    __tablename__ = "channels"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    created_by: Mapped[str] = mapped_column(foreign_key="users.id")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
