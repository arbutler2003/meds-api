from fastapi import FastAPI, HTTPException
from app.services.fda_client import fetch_drug_label


app = FastAPI()


@app.get("/drug/{name}")
async def get_drug_info(name: str):
    data = await fetch_drug_label(name)

    if not data:
        raise HTTPException(status_code=404, detail=f"Drug '{name}' not found.")

    return data