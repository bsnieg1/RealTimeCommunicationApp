from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._channel_connections: dict[int, set[WebSocket]] = defaultdict(set)
        self._connection_user: dict[WebSocket, int] = {}

    def connect(self, websocket: WebSocket, user_id: int) -> None:
        self._connection_user[websocket] = user_id

    def disconnect(self, websocket: WebSocket) -> None:
        self._connection_user.pop(websocket, None)
        for connections in self._channel_connections.values():
            connections.discard(websocket)

    def subscribe(self, websocket: WebSocket, channel_id: int) -> None:
        self._channel_connections[channel_id].add(websocket)

    def unsubscribe(self, websocket: WebSocket, channel_id: int) -> None:
        self._channel_connections[channel_id].discard(websocket)

    async def broadcast(self, channel_id: int, message: dict) -> None:
        for websocket in self._channel_connections.get(channel_id, set()):
            await websocket.send_json(message)


manager = ConnectionManager()
