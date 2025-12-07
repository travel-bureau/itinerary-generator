import hashlib
import json
import os
import re

import redis

def initialize_redis():
    global redis_client
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        decode_responses=False,
        username=os.getenv("REDIS_USERNAME"),
        password=os.getenv("REDIS_PASSWORD"),
    )

# Load ChatGPT cache
def load_chatgpt_cache(input_data: dict) -> dict | None:
    key = _hash_key(input_data)
    print("🔍 Hash key:", key)
    cached = redis_client.get(key)
    return json.loads(cached) if cached else None

# Save ChatGPT cache
def save_chatgpt_cache(input_data: dict, response_data):
    key = _hash_key(input_data)
    redis_client.set(key, json.dumps(response_data), ex=5184000)  # 60-day TTL

def delete_chatgpt_cache(input_data: dict) -> bool:
    key = _hash_key(input_data)
    result = redis_client.delete(key)
    return result == 1  # Returns True if key was deleted, False if not found


# ======= Utilities =======

def normalize_text(text: str) -> str:
    # Remove extra spaces, normalize line breaks
    text = re.sub(r'\s+', ' ', text.strip())
    return text.lower()  # optional: case-insensitive matching

def _hash_key(text: str) -> str:
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode()).hexdigest()