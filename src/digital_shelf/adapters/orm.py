from digital_shelf.domain import model

from sqlalchemy import Column, Integer, String, Table, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import registry

mapper_registry = registry()
metadata = mapper_registry.metadata

products = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(255)),
    Column("qty", Integer, nullable=False),
    Column("expiry_date", DateTime, nullable=False),
    Column("nutrition_facts", JSONB, nullable=True),
    UniqueConstraint("name","expiry_date", name="uq_product_name_expiry")
)

def start_mappers():
    mapper_registry.map_imperatively(model.Product, products)