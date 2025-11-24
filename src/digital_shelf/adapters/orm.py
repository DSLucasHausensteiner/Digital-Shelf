
from sqlalchemy import Column, Integer, Float, String, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase

from digital_shelf.domain.model import Product, Unit
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

    def _to_domain(self) -> Product:
        size = None
        if self.size_amount is not None or self.size_unit is not None:
            size = Unit(amount=self.size_amount, unit=self.size_unit)

        return Product(
            name=self.name,
            qty=self.qty,
            size=size,
            expiry_date=self.expiry_date,
            nutrition_facts=self.nutrition_facts,
        )
