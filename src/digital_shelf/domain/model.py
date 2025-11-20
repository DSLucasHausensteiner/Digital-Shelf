from typing import Optional
from dataclasses import dataclass
from pydantic import BaseModel
from datetime import datetime

class Unit(BaseModel):
    amount: Optional[float] = None
    unit: Optional[str] = None


class Product(BaseModel):
    name: Optional[str] = None
    qty: Optional[int] = None
    size: Optional[Unit] = None
    expiry_date: Optional[datetime] = None
    nutrition_facts:Optional[dict] = {}