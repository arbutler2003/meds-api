import json
import os

import httpx
import redis.asyncio as redis
from dotenv import load_dotenv


load_dotenv()

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


async def fetch_drug_label(drug_name: str) -> dict | None:
    """
    Fetches the raw 'results' from the FDA API, currently omits the 'meta' data.

    Args:
        drug_name: The brand/generic name (case-insensitive) of the drug being searched for.
    Returns:
        The raw 'results' from the FDA API or None (if fails).
    """
    base_url = "https://api.fda.gov/drug/label.json"

    search_query = f'openfda.brand_name:"{drug_name}" + openfda.generic_name:"{drug_name}"'

    params = {
        "api_key": os.getenv("FDA_API_KEY"),
        "search": search_query,
        "limit": 1
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(base_url, params=params)

        except httpx.RequestError as e:
            print(f"Request error: {e}")
            return None

        if response.status_code == 404:
            print(f"{drug_name} not found.")
            return None

        data = response.json()
        results = data.get("results")

        if results and isinstance(results, list) and len(results) > 0:
            return results[0]

        return None


async def fetch_drug_label_with_caching(drug_name: str) -> dict | None:
    """
    Fetches drug label from the FDA API or a Redis cache if available (stored for 24 hours).

    This function operates above fetch_drug_label(), checking the Redis cache first before fetching from the API and
    storing the response in the cache.

    Args:
        drug_name: The brand/generic name (case-insensitive) of the drug being searched for.
    Returns:
        The 'results' from the FDA drug label API as a dictionary or None (if fails).
    """
    cache_key = f"drug_label:{drug_name.lower()}"

    try:
        cached_response = await redis_client.get(cache_key)
        if cached_response:
            print(f"Cache hit for {drug_name}")
            return json.loads(cached_response) # Deserialize
    except redis.RedisError as e:
        print(f"Redis error: {e}")

    print(f"Cache miss for {drug_name}. Fetching...")
    fresh_response = await fetch_drug_label(drug_name)

    if fresh_response:
        await redis_client.set(
            cache_key,
            json.dumps(fresh_response), # Serialize
            ex=86400 # 24 hours
        )

    return fresh_response