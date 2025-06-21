# Create this application in CORTEX_AI_DB
# Import the packages from the Package List.txt into this Streamlit app (Packages -> Find Packages)
# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
from PIL import Image

st.set_page_config(layout="wide")
session = get_active_session()

st.title("AI-Powered Menu Intelligence using Image Recognition and Classification")


prompt = """Classify the food image {0} into: 
        1. Item (Noodles, Fried rice, Burger, Pizza etc.,),
        2. Meal Type (Breakfast, Lunch, or Dinner), 
        3. Cuisine (e.g., American, Indian, Italian, Chinese), 
        4. Type (Vegetarian or Non-Vegetarian). 
        
        Write a short, catchy, restaurant-style description in **italics** in an attribute called "Description" within 40 words.
        Strictly, Provide the above 5 with **Bold headers** line by line.
        
        Avoid using sentences like,
        Heres the classification: , For this image of a coffee/tea beverage:
        Do not give JSON output
        """

if st.button("Load and Classify Menu Item Images from Stage"):
    
    data = session.sql(f"""CREATE OR REPLACE TABLE MENU_ITEM_IMAGES_CLASSIFIED AS
                        SELECT RELATIVE_PATH, SNOWFLAKE.CORTEX.COMPLETE('pixtral-large',
                        PROMPT('{prompt}',
                        TO_FILE('@MULTIMODAL_DEMO_STG', RELATIVE_PATH))) as image_classification
                        FROM DIRECTORY(@CORTEX_AI_DB.PUBLIC.MULTIMODAL_DEMO_STG)""");
    
    ls = data.collect()
    st.success("Images classified and loaded successfully!")


table_check = session.sql("""
    SELECT COUNT(*) AS COUNT
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_SCHEMA = 'PUBLIC' 
    AND TABLE_NAME = 'MENU_ITEM_IMAGES_CLASSIFIED'
""").collect()

if table_check[0]['COUNT'] == 0:
    st.info("Please click **'Load and Classify Menu Item Images from Stage'** first to create the classified images table.")
else:
    # Table exists, continue loading images
    Img = session.sql("ls @MULTIMODAL_DEMO_STG").collect()
    Img_lst = [row["name"].split("/")[-1] for row in Img]
    lss = st.selectbox("Select Image", [None] + Img_lst)

    menu_classified = session.sql("SELECT * FROM CORTEX_AI_DB.PUBLIC.MENU_ITEM_IMAGES_CLASSIFIED").collect()
    df = pd.DataFrame(menu_classified)

    if lss is not None:
        c1, c2, c3 = st.columns([0.3, 0.5, 0.2])

        with c2:
            image = session.file.get_stream(f"@cortex_ai_db.public.MULTIMODAL_DEMO_STG/{lss}", decompress=False).read()

            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.image(image, use_container_width=False)

            df = df[df['RELATIVE_PATH'] == lss]
            classification_text = df['IMAGE_CLASSIFICATION'].iloc[0]
            st.write(f"### {classification_text}")
            st.markdown("</div>", unsafe_allow_html=True ) 
