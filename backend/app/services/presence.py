import json 

from app.services.redis_client import redis_client


PRESENCE_CHANNEL = "presence"
ONLINE_SET_KEY = "presence:online"



async def mark_online(user_id: int) -> None:
    await redis_client.sadd(ONLINE_SET_KEY, user_id)
    await redis_client.publish(
        PRESENCE_CHANNEL, json.dumps({"type": "presence.update", "user_id": user_id, "status": "online"})
    )


async def mark_offline(user_id: int) -> None:
    await redis_client.srem(ONLINE_SET_KEY, user_id)
    await redis_client.publish(
        PRESENCE_CHANNEL, json.dumps({"type": "presence.update", "user_id": user_id, "status": "offline"})
    )