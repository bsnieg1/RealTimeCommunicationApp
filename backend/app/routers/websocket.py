from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, WebSocketException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database import get_db
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate
from app.services.connection_manager import manager
from app.services.membership import require_membership

router = APIRouter(tags=["websocket"])


def _message_new_payload(message: Message) -> dict:
    return {
        "type": "message.new",
        "id": message.id,
        "channel_id": message.channel_id,
        "sender_id": message.sender_id,
        "content": message.content,
        "client_message_id": message.client_message_id,
        "created_at": message.created_at.isoformat(),
    }


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except Exception:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    user = await db.get(User, user_id)
    if user is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    await websocket.accept()
    manager.connect(websocket, user.id)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            try:
                if msg_type == "subscribe":
                    channel_id = data["channel_id"]
                    await require_membership(channel_id, user.id, db)
                    manager.subscribe(websocket, channel_id)

                elif msg_type == "message.send":
                    body = MessageCreate(**data)
                    await require_membership(body.channel_id, user.id, db)

                    existing = await db.scalar(
                        select(Message).where(
                            Message.sender_id == user.id,
                            Message.client_message_id == body.client_message_id,
                        )
                    )
                    if existing is not None:
                        await websocket.send_json(_message_new_payload(existing))
                        continue

                    message = Message(
                        channel_id=body.channel_id,
                        sender_id=user.id,
                        content=body.content,
                        client_message_id=body.client_message_id,
                    )
                    db.add(message)
                    await db.commit()
                    await db.refresh(message)

                    await manager.broadcast(body.channel_id, _message_new_payload(message))

                else:
                    await websocket.send_json({"type": "error", "detail": f"Unknown message type: {msg_type}"})

            except HTTPException as exc:
                await websocket.send_json({"type": "error", "detail": exc.detail})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
