# Create this application in CORTEX_AI_DB
# Import the packages from the Package List.txt into this Streamlit app (Packages -> Find Packages)
# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from PIL import Image
import pandas as pd
import _snowflake
import json



st.set_page_config(layout="wide")

st.markdown("""<style>
            button[data-testid="baseButton-secondary"] {
                background-color: #00008B; /* Green */
                color: white;
                padding: 8px 18px;
                border: none;
                border-radius: 24px;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s ease, transform 0.2s ease;
            }
            button[data-testid="baseButton-secondary"]:hover {
                background-color: #80BFFF; /* Slightly darker green */
                transform: scale(1.05); /* Slight zoom effect */
            }
            /* Style when the button is clicked (active) */
            button[data-testid="baseButton-secondary"]:active {
                background-color: #0059B3; /* Darker green */
                transform: scale(0.98); /* Slight shrink effect */
                box-shadow: 0 5px #666; 
            }

</style>""", unsafe_allow_html=True)

# Define options
options = ['Employee Churn Prediction']

# Set up sidebar with radio buttons for options
option = st.sidebar.radio('Select Dashboard', options)

if option == 'Employee Churn Prediction':
     
    session = get_active_session()
    result = session.table("CORTEX_AI_DB.PUBLIC.CALL_CENTER_EMPLOYEE_CHURN")
    data_list = result.collect()
    df = pd.DataFrame(data_list)
    df=df.drop(columns=['EMPLOYEE_ID','CHURN'],axis=1)
    

    c1, c2, c3 = st.columns([0.35,0.5,0.1])
    with c2:
        st.header("Call Center Employee Churn Prediction")

    st.write(' ')
    st.write(' ')
    st.subheader('Data Preview')
    st.dataframe(df.head())
    
    if st.button('Predict '):
        session3 = get_active_session()
        rs = session3.sql("""CREATE OR REPLACE TABLE EMPLOYEE_CHURN_OUT AS
        SELECT * EXCLUDE prediction,prediction:class AS pred_class,round(prediction['probability'][prediction:class], 3) as probability FROM EMPLOYEE_CHURN_PREDICTION;
        """)
        rs.collect()
        
        rs1=session.table("CORTEX_AI_DB.PUBLIC.EMPLOYEE_CHURN_OUT")
        ls = rs1.collect()
        dat_f = pd.DataFrame(ls)
        # # dat_f = dat_f.drop(columns=['TARGET_CHURN_FLAG'], axis=1)
        st.dataframe(dat_f)

       
        session3.close()