from digital_shelf.domain import model

from sqlalchemy import Column, Integer, Float, String, Table, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import registry

mapper_registry = registry()
metadata = mapper_registry.metadata

products = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(255), nullable=False),
    Column("qty", Integer, nullable=False),
    Column("size_amount", Float, nullable=True),
    Column("size_unit", String("10"), nullable=True),
    Column("expiry_date", DateTime, nullable=True),
    Column("nutrition_facts", JSONB, nullable=True),
    UniqueConstraint(
        "name", "expiry_date", "size_amount", "size_unit",
        name="uq_product_unique_item"
    )
)

def start_mappers():
    mapper_registry.map_imperatively(model.Product, products)

start_mappers()