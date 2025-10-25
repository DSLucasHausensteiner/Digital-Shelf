import base64
import io
import streamlit as st
import pandas as pd
import requests

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

def process_grocery_img(image: io.BytesIO):

    base64_img = base64.b64encode(image).decode("utf-8")

    request_dict = {
    "file": base64_img,
    "fileType": 1,
    "useDocOrientationClassify": True,
    "useDocUnwarping": True,
    "useTextlineOrientation": True,
    "textDetLimitSideLen": 960,
    "textDetLimitType": "max",
    "textDetThresh": 0.3,
    "textDetBoxThresh": 0,
    "textDetUnclipRatio": 1.6,
    "textRecScoreThresh": 0,
    "visualize": True
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(
        url="http://192.168.178.52:8080/ocr",
        json=request_dict,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    response_json = response.json()

    result_texts=[]

    ocr_results = response_json["result"]["ocrResults"]

    for ocr_result in ocr_results:
        result_texts.extend(ocr_result["prunedResult"]["rec_texts"])

    return result_texts


st.title("Digital Shelf")

st.write("Welcome to the digital version of your shelf.")

with st.expander(label="Enter a new product"):
    img = st.camera_input(label="Take a photo of a grocery item")
    
    if img is not None:
        texts = process_grocery_img(img.read())
        texts = " ".join(texts)
        st.write(f"Found texts are {texts}")

    with st.form("New Grocery item"):
        label = st.text_input("Enter the name of the product")
        expiry_date = st.date_input("Enter the expiry date") 
        qnty = st.number_input("Enter the quantity of the product")
        submitted = st.form_submit_button("Submit")
        if submitted: ...
    # with Session(engine) as session:
    #     # Create domain objects
    #     prod1 = Product(name="Cereal", qty=10, expiry_date=datetime(2025,12,10))
    #     # prod2 = Product(name="Milk", qty=25, expiry_date=datetime(2025,10,10))

    #     add_or_update_product(session, prod1)
    #     # add_or_update_product(session, prod2)

        
    #     session.commit()

if st.button(label="View my digital shelf"):
    with Session(engine) as session:
        products_list = session.query(products).all()
        df = pd.DataFrame(products_list, columns=["ID", "Name", "Quantity", "Expiry_Date", "Nutrition Facts"])
        st.write(df)


st.button(label="Generate Recipe")