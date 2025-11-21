
from sqlalchemy import Column, Integer, Float, String, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class ProductORM(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    qty = Column(Integer, nullable=False)

    size_amount = Column(Float)
    size_unit = Column(String(10))

    expiry_date = Column(DateTime)
    nutrition_facts = Column(JSONB)

    __table_args__ = (
        UniqueConstraint(
            "name", "expiry_date", "size_amount", "size_unit",
            name="uq_product_unique_item"
        ),
    )
