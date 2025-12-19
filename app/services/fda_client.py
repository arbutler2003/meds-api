import os
import httpx
from dotenv import load_dotenv


load_dotenv()


async def fetch_drug_label(drug_name: str):
    BASE_URL = "https://api.fda.gov/drug/label.json"

    params = {
        "api_key": os.getenv("FDA_API_KEY"),
        "search": f'openfda.brand_name:"{drug_name}"',
        "limit": 1
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BASE_URL, params=params)

        except httpx.RequestError as e:
            print(f"Request error: {e}")
            return None

        if response.status_code == 404:
            print(f"{drug_name} not found.")
            return None

        return response.json()