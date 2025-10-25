from dataclasses import dataclass
from pydantic import BaseModel
from datetime import datetime

class Product(BaseModel):
    name: str
    qty: int
    expiry_date: datetime
    nutrition_facts: dict