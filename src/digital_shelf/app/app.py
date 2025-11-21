import base64
import io
import streamlit as st
import pandas as pd
import requests
import hashlib
from datetime import datetime

from openai import OpenAI

from digital_shelf.adapters.orm import Base
from digital_shelf.domain.model import Product, Unit
from digital_shelf.adapters.repository import ProductRepository

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Setup ORM
@st.cache_resource()
def get_engine():
    engine = create_engine("postgresql://postgres:secret@127.0.0.1:5433")#db:5432")#
    Base.metadata.create_all(engine)

    return engine

engine = get_engine()


client = OpenAI(
    base_url="http://localhost:11434/v1",#ollama:11434/v1",#
    api_key="dummy-key",
)

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

def render_image_container(index, image):
    with st.container(border=True, horizontal=True):
            st.image(image, width=76)
            with st.expander("🔍 Open full-size"):
                st.image(image)
            if st.button(label="", icon=":material/delete:", key=f"delete_{index}"):
                st.session_state.images.pop(index)
                st.rerun()

def extract_product_info_with_llm(ocr_texts: str):
    """
    ocr_texts: list of strings, one per image.
    returns: Pydantic-validated ExtractionResult
    """

    system_prompt = """
        You are an OCR post-processing assistant for grocery receipts and product photos.
        Your goal is to clean noisy OCR text and extract structured product information.

        You will ALWAYS return ONLY a valid JSON object matching this schema:

        {
        "name": "string",
        "qty": int,
        "size": {
            "amount": float,
            "unit": "g" | "kg" | "ml" | "l" | null
        },
        "expiry_date": "ISO8601 date string or null",
        "nutrition_facts": { "key": "value", ... }
        }

        ### TASK
        Given messy OCR or user text, extract the best possible structured information.
        The OCR may contain:
        - missing fields
        - wrong separators (e.g., “1 . 5 L” or “500G”)
        - inconsistent units (g/G/GR/grm)
        - multiple numbers with unclear meaning
        - wrong or ambiguous dates (e.g., “12/02/25”)
        - no date at all
        - irrelevant text (ads, coupons, unrelated items)
        - german or english text

        You MUST:
        1. Infer the most likely product *name*.  
        - The name must be grammatically correct in the language detected from the input.
        - Automatically correct missing umlauts and OCR mistakes (e.g., "fur" → "für", "Kakao fur Getranke" → "Kakao für Getränke").
        - Fix broken compound words (e.g., "Getranke" → "Getränke") and capitalization.
        - The name should sound like a real product name as sold in a supermarket.
        - Never copy OCR mistakes literally — always normalize wording.
        2. Normalize and infer *qty* (how many items):
        - If no explicit quantity → default to 1.
        - If ranges or multipacks (“3x200ml”) → qty=3 and size.amount=200 and size.unit="ml".
        3. Parse *size* (amount + unit):
        - Accept formats like: “500g”, “0.5 kg”, “1,5L”, “330 ML”, “2x1L”.
        - Normalize units to one of: "g", "kg", "ml", "l".
        4. Parse *expiry_date* into a valid ISO8601 format (“YYYY-MM-DD”):
        - Handle formats: DD/MM/YY, MM-DD-2025, 2025.03.10, 10/12/25, etc.
        - If ambiguous (e.g. “01/02/03”), infer the most realistic for groceries (DD/MM/YY).
        - If missing → set expiry_date=null.
        5. Extract nutrition facts if present, as a dictionary.
        - Keys should be lowercase and cleaned (“fat 3g”, “carbs 12g”, etc.).
        - OCR noise should be removed.
        
        If ANY value is fully unknowable, set it to null — NEVER guess wildly!

        ### OUTPUT RULES
        - Output ONLY the JSON object. No markdown. No explanation.
        - JSON must strictly follow the schema.
        - Never invent unrealistic values.

        """
    user_prompt = f"""
        Here is text extracted from one or more grocery product images or receipts:

        {ocr_texts}

        Extract all information you can identify and output ONLY JSON,
        no extra text, no explanations.
        Missing fields must be null, not empty strings.
        """
    response = client.chat.completions.create(
        model="qwen2.5:7b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    content = response.choices[0].message.content

    # Validate & parse with Pydantic
    st.write(content)
    result = Product.model_validate_json(content)
    return result
    
# Setup sessions states
if "images" not in st.session_state:
    st.session_state.images = []

if "image_expander" not in st.session_state:
    st.session_state.image_expander = False

if "last_image_hash" not in st.session_state:
    st.session_state.last_image_hash = None

if "current_product" not in st.session_state:
    st.session_state.current_product = None

st.session_state.setdefault("form_nutrition_facts")

st.title("Digital Shelf 1")

st.write("Welcome to the digital version of your shelf.")
st.write(st.session_state.image_expander)

with st.expander(label="Enter a new product", expanded=st.session_state.image_expander):
    # Image capture to get the images
    img = st.camera_input(
        "Take a photo of a grocery item",
        on_change=lambda: st.session_state.update({"image_expander": True})
    )


    if img is not None:
        img_bytes = img.read()
        img_hash = hashlib.md5(img_bytes).hexdigest()

        if img_hash != st.session_state.last_image_hash:
            st.session_state.images.append(img_bytes)
            st.session_state.last_image_hash = img_hash

    for i, img_bytes in enumerate(st.session_state.images):
        render_image_container(i, img_bytes)

    if st.button(label="Extract the text from the entered Images"):
        processed_texts = ""
        for img in st.session_state.images:
            texts = process_grocery_img(img)
            joined_texts = " ".join(texts)
            processed_texts += joined_texts
        st.write(f"Found texts are: \n\n {processed_texts}")


        try:
            result = extract_product_info_with_llm(processed_texts)
        except Exception as e:
            st.error(f"Failed to parse LLM output as valid JSON: {e}")
        else:
            # Show raw JSON
            st.subheader("Structured extraction (Pydantic)")
            st.session_state.current_product = result
            st.json(st.session_state.current_product)
            st.session_state.form_name = result.name
            st.session_state.form_expiry = result.expiry_date
            st.session_state.form_qty = result.qty
            st.session_state.form_size_amount = result.size.amount
            st.session_state.form_size_unit = result.size.unit
            st.session_state.form_nutrition_facts = result.nutrition_facts


    with st.form("New Grocery item"):
        name = st.text_input("Enter the name of the product", key="form_name")
        expiry_date = st.date_input("Enter the expiry date", key="form_expiry")
        qty = st.number_input("Enter the quantity of the product", key="form_qty", step=1)
        size_amount = st.number_input("Enter an amount of the product", key="form_size_amount")
        size_unit = st.selectbox("Enter the unit of the amount", options=["g", "kg", "ml", "l"], key="form_size_unit")

        nutrition_facts = None
        if st.session_state.form_nutrition_facts is not None:
            nutrition_df = pd.DataFrame(st.session_state.form_nutrition_facts)
            nutrition_facts = st.data_editor(nutrition_df)

        p = Product(
            name=name,
            expiry_date=expiry_date,
            qty=qty,
            size=Unit(amount=size_amount, unit=size_unit),
            nutrition_facts= nutrition_facts
        )

        submitted = st.form_submit_button("Submit")
        if submitted:
            with Session(engine) as session:
                # Create domain objects
                repo = ProductRepository(session)
                repo.add_or_update(p)

if st.button(label="View my digital shelf"):
    with Session(engine) as session:
        # Create domain objects
        repo = ProductRepository(session)
        products_list = repo.list_all()
        product_dicts = [p.model_dump() for p in products_list]
        df = pd.DataFrame(product_dicts)
        df = df.rename(columns={
            "name": "Name",
            "qty": "Quantity",
            "size": "Size",
            "expiry_date": "Expiry Date",
            "nutrition_facts": "Nutrition Facts",
        })
        st.write(df)


st.button(label="Generate Recipe")