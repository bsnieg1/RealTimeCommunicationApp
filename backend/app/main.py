import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.dependencies import get_current_user
from app.routers import auth, users, channels, messages, websocket
from app.schemas.auth import UserResponse
from app.services.connection_manager import manager
from app.services.presence import PRESENCE_CHANNEL
from app.services.redis_client import redis_client


async def _presence_listener() -> None:
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(PRESENCE_CHANNEL)
    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        await manager.broadcast_all(json.loads(message["data"]))


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_presence_listener())
    yield
    task.cancel()


app = FastAPI(title="Real-Time Chat API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(channels.router)
app.include_router(messages.router)
app.include_router(websocket.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/me", response_model=UserResponse)
def read_current_user(user=Depends(get_current_user)):
    return user
