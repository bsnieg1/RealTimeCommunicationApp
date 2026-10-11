import json
import asyncio
import pytest
import websockets

BASE_WS = "ws://127.0.0.1:8000/ws"


@pytest.mark.asyncio
async def test_broadcast_reaches_all_members_with_same_id(token1, token2, channel_id):
    async with websockets.connect(f"{BASE_WS}?token={token1}") as ws1, \
               websockets.connect(f"{BASE_WS}?token={token2}") as ws2:
        await ws1.send(json.dumps({"type": "subscribe", "channel_id": channel_id}))
        await ws2.send(json.dumps({"type": "subscribe", "channel_id": channel_id}))

        await ws1.send(json.dumps({
            "type": "message.send", "channel_id": channel_id,
            "content": "order test", "client_message_id": "order-1",
        }))

        msg1 = json.loads(await ws1.recv())
        msg2 = json.loads(await ws2.recv())
        assert msg1["id"] == msg2["id"]


@pytest.mark.asyncio
async def test_retry_does_not_rebroadcast(token1, token2, channel_id):
    async with websockets.connect(f"{BASE_WS}?token={token1}") as ws1, \
               websockets.connect(f"{BASE_WS}?token={token2}") as ws2:
        await ws1.send(json.dumps({"type": "subscribe", "channel_id": channel_id}))
        await ws2.send(json.dumps({"type": "subscribe", "channel_id": channel_id}))

        payload = {
            "type": "message.send", "channel_id": channel_id,
            "content": "dedup test", "client_message_id": "dedup-1",
        }
        await ws1.send(json.dumps(payload))
        first = json.loads(await ws1.recv())
        await ws2.recv()

        await ws1.send(json.dumps(payload)) 
        retry = json.loads(await ws1.recv())
        assert retry["id"] == first["id"] 

        with pytest.raises(TimeoutError):
            await asyncio.wait_for(ws2.recv(), timeout=1.0) 
