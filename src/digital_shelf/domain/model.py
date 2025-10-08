from dataclasses import dataclass
from datetime import datetime

class Product:
    name: str
    qty: int
    expiry_date: datetime
    nutrition_facts: dict