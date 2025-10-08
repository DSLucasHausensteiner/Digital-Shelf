from datetime import datetime
import streamlit as st
import pandas as pd

from digital_shelf.adapters.orm import metadata, start_mappers, products
from digital_shelf.domain.model import Product
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

# Setup ORM
@st.cache_resource()
def get_engine_and_mappers():
    engine = create_engine("postgresql://postgres:secret@127.0.0.1:5433")
    metadata.create_all(engine)
    start_mappers()
    return engine

engine = get_engine_and_mappers()

# Functions to add products
def add_or_update_product(_session: Session, product: Product):
    query = insert(products).values(name=product.name, qty=product.qty, expiry_date=product.expiry_date)
    query = query.on_conflict_do_update(
        index_elements=["name", "expiry_date"],
        set_={"qty": products.c.qty + product.qty},
    )
    _session.execute(query)

st.title("Digital Shelf")

st.write("Welcome to the digital version of your shelf.")

if st.button(label="Enter a new product"):
    with Session(engine) as session:
        # Create domain objects
        prod1 = Product(name="Cereal", qty=10, expiry_date=datetime(2025,12,10))
        # prod2 = Product(name="Milk", qty=25, expiry_date=datetime(2025,10,10))

        add_or_update_product(session, prod1)
        # add_or_update_product(session, prod2)

        
        session.commit()

if st.button(label="View my digital shelf"):
    with Session(engine) as session:
        products_list = session.query(products).all()
        df = pd.DataFrame(products_list, columns=["ID", "Name", "Quantity", "Expiry_Date"])
        st.write(df)

st.button(label="Generate Recipe")