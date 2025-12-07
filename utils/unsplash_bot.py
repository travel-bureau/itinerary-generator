import os
from io import BytesIO

import requests

def initialize_unsplash():
    global IMAGE_CACHE_DIR, UNSPLASH_ACCESS_KEY, PLACEHOLDER_IMAGE
    CACHE_DIR = "cache"
    IMAGE_CACHE_DIR = os.path.join(CACHE_DIR, "images")
    UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
    PLACEHOLDER_IMAGE = BytesIO(requests.get("https://images.unsplash.com/photo-1559311648-d46f5d8593d6?q=80&w=3500&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D").content)
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)

def fetch_image(query):
    """Fetch image from Unsplash or return cached/fallback image."""
    safe_query = query.replace(' ', '_')
    cache_path = os.path.join(IMAGE_CACHE_DIR, f"{safe_query}.jpg")
    if os.path.exists(cache_path):
        with open(cache_path, 'rb') as f:
            return BytesIO(f.read())
    try:
        url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_ACCESS_KEY}"
        resp = requests.get(url)
        if resp.status_code == 200:
            img_url = resp.json()["urls"]["regular"]
            img_data = requests.get(img_url).content
            with open(cache_path, 'wb') as f:
                f.write(img_data)
            return BytesIO(img_data)
    except Exception:
        pass
    return PLACEHOLDER_IMAGE