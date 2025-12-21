from pydantic import BaseModel


class RefinedDrugLabel(BaseModel):
    """
    Defines the fields displayed in the refined drug label.
    These fields (and most others) in this api are wrapped in a list, even if there is only one value.
    """
    brand_name: str
    generic_name: str
    purpose: str
    indications: str
    warnings: str
    interactions: str
