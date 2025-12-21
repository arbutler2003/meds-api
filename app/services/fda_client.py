import os
import httpx
from dotenv import load_dotenv


load_dotenv()


async def fetch_drug_label(drug_name: str) -> dict | None:
    """
    Fetches the raw 'results' from the FDA API, currently omits the 'meta' data.

    :param drug_name: The brand/generic name (case-insensitive) of the drug being searched for.
    :return: The raw 'results' from the FDA API or None (if fails).
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