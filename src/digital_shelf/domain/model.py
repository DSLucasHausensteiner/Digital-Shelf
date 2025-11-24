from typing import Optional
from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class Unit(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    amount: Optional[float] = None
    unit: Optional[str] = None


class Product(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    qty: Optional[int] = None
    size: Optional[Unit] = None
    expiry_date: Optional[datetime] = None
    nutrition_facts:Optional[dict] = {}