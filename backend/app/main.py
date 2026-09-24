from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.dependencies import get_current_user
from app.routers import auth, users, channels, messages, websocket

app = FastAPI(title="Real-Time Chat API")

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


@app.get("/me")
def read_current_user(user=Depends(get_current_user)):
    return user
