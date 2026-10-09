from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)) -> User:
    existing = await db.scalar(
        select(User).where((User.username == body.username) | (User.email == body.email))
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already registered")

    user = User(
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password)
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user