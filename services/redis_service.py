import redis
import json

MAX_MESSAGE = 20


class RedisService:
    def __init__(self, host="localhost", port=6379):
        self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)

    def get_redis(self, userid: int):
        state_json = self.redis_client.get(f"session_{userid}")
        if state_json:
            state = json.loads(state_json)
            if isinstance(state, dict):
                self.title = state.get("title")
                return state
            else:
                return {"messages": state}
        return {"messages": [], "title": None}

    def set_redis(self, userid: int, result: dict, title: str):
        session_id = f"session_{userid}"
        if result.get("messages") and len(result.get("messages")) > MAX_MESSAGE:
            updated_list_of_messages = result.get("messages")[-MAX_MESSAGE:]
        else:
            updated_list_of_messages = result.get("messages")

        self.redis_client.set(
            session_id,
            json.dumps({"messages": updated_list_of_messages, "title": title}),
        )
