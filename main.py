from fastapi import FastAPI, HTTPException

from app.schemas import RefinedDrugLabel
from app.services import fetch_drug_label


app = FastAPI()


def extract_text(data: dict, key: str) -> str:
    """
    Extracts text, which in this API is generally a list of strings and possibly a single string.

    :param data: The dictionary containing drug label response.
    :param key: The key to extract text from.
    :return:
    """
    value = data.get(key)

    if value is None:
        return "Unknown"

    if isinstance(value, list):
        return " ".join(value)

    if isinstance(value, str):
        return value

    return "Unknown"

@app.get("/drug/{name}", response_model=RefinedDrugLabel)
async def get_drug_info(name: str) -> dict:
    """
    Retrieves a refined drug label from the FDA API.

    :param name: The brand/generic drug name (case-insensitive).
    :return: A refined drug label as a JSON object
    """
    raw_data = await fetch_drug_label(name)

    if not raw_data:
        raise HTTPException(status_code=404, detail="Drug not found.")

    # Nested dictionary containing the brand and generic names.
    openfda = raw_data.get("openfda", {})

    return {
        "brand_name": extract_text(openfda, "brand_name"),
        "generic_name": extract_text(openfda, "generic_name"),
        "purpose": extract_text(raw_data, "purpose"),
        "indications": extract_text(raw_data, "indications_and_usage"),
        "warnings": extract_text(raw_data, "warnings"),
        "interactions": extract_text(raw_data, "drug_interactions")
    }