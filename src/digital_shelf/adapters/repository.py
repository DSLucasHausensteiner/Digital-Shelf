from sqlalchemy.dialects.postgresql import insert
from digital_shelf.adapters.orm import ProductORM
from digital_shelf.domain.model import Product

class ProductRepository():
    def __init__(self, session):
        self.session = session
    
    def add_or_update(self, p: Product):
        table = ProductORM.__table__

        query = insert(table).values(
            name=p.name,
            qty=p.qty,
            size_amount=p.size.amount if p.size else None,
            size_unit=p.size.unit if p.size else None,
            expiry_date=p.expiry_date,
            nutrition_facts=p.nutrition_facts,

        )
        query = query.on_conflict_do_update(
            index_elements=["name", "expiry_date", "size_amount", "size_unit"],
            set_={"qty": table.c.qty + p.qty},
        )
        self.session.execute(query)
        self.session.commit()
    
    def list_all(self):
        rows = self.session.query(ProductORM).all()
        return [self._to_domain(row) for row in rows]

    
    def _to_domain(self, orm: ProductORM) -> Product:
        return Product.model_validate(orm)

    def _to_orm(self, p: Product) -> ProductORM:
        return ProductORM(
            name=p.name,
            qty=p.qty,
            size_amount=p.size.amount if p.size else None,
            size_unit=p.size.unit if p.size else None,
            expiry_date=p.expiry_date,
            nutrition_facts=p.nutrition_facts
        )