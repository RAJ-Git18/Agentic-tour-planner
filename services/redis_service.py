from redis.asyncio import Redis
import json
import hashlib

from config import settings

MAX_MESSAGE = settings.REDIS_MAX_MESSAGES


class RedisService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def get_redis(self, userid: int):
        state_json = await self.redis_client.get(f"session_{userid}")
        if state_json:
            state = json.loads(state_json)
            if isinstance(state, dict):
                return state
            else:
                return {"messages": state}
        return {"messages": [], "title": None}

    async def set_redis(self, userid: int, result: dict, title: str):
        session_id = f"session_{userid}"
        messages = result.get("messages", [])

        if len(messages) > MAX_MESSAGE:
            updated_list_of_messages = messages[-MAX_MESSAGE:]
        else:
            updated_list_of_messages = messages

        await self.redis_client.set(
            session_id,
            json.dumps({"messages": updated_list_of_messages, "title": title}),
        )

    async def set_emb_cache(self, user_query: str, embedding: list):
        norm_user_query = user_query.strip().lower()
        key = f"embedding:{hashlib.sha256(norm_user_query.encode()).hexdigest()}"
        await self.redis_client.set(key, json.dumps(embedding), ex=86400)

    async def get_emb_cache(self, user_query: str):
        norm_user_query = user_query.strip().lower()
        key = f"embedding:{hashlib.sha256(norm_user_query.encode()).hexdigest()}"
        cached_data = await self.redis_client.get(key)
        return json.loads(cached_data) if cached_data else None
