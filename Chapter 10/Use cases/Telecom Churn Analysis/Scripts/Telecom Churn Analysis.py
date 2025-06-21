# Create this application in CORTEX_AI_DB
# Import the packages from the Package List.txt into this Streamlit app (Packages -> Find Packages)
# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd

st.set_page_config(layout="wide")

session = get_active_session()
result = session.table("CORTEX_AI_DB.PUBLIC.TELECOM_CHURN")
data_list = result.collect()
df = pd.DataFrame(data_list)
df=df.drop(columns=['CHURN_FLAG'],axis=1)


c1, c2, c3 = st.columns([0.35,0.5,0.1])
with c2:
    st.header("Telecom Churn Prediction")

st.write(' ')
st.write(' ')
st.subheader('Data Preview')
st.dataframe(df.head())

if st.button('Predict '):
    session3 = get_active_session()
    rs = session3.sql(""" CREATE OR REPLACE TABLE TELECOM_CHURN_PREDICTION_OUT AS
                            SELECT * EXCLUDE prediction,prediction:class AS pred_class,round(prediction['probability'][prediction:class], 3) as probability 
                            FROM TELECOM_CHURN_PREDICTION;
                        """)
    ls = rs.collect()
    
    prompt = f"""
    You are provided with a dataset containing telecom customer churn predictions.  
    
    Analyze the attributes and provide the **top 2 reasons** why this customer is likely to **churn**.
    Clearly mention the column names used in your reasoning based on the list of columns below.
    
    **Columns :**
    TENURE_MONTHS is ###',TENURE_MONTHS,'###,
    MONTHLY_CHARGES is ###',MONTHLY_CHARGES,'###,
    TOTAL_CHARGES is ###',TOTAL_CHARGES,'###,
    CONTRACT_TYPE is ###',CONTRACT_TYPE ,'###,
    PAYMENT_METHOD is ###',PAYMENT_METHOD ,'###,
    HAS_PAPERLESS_BILLING is ###',HAS_PAPERLESS_BILLING ,'###,
    IS_SENIOR_CITIZEN is ###',IS_SENIOR_CITIZEN ,'###,
    DATA_USAGE_GB is ###',DATA_USAGE_GB,'###,
    STREAMING_USAGE_LEVEL is ###',STREAMING_USAGE_LEVEL ,'###,
    NUM_SERVICES is ###',NUM_SERVICES,'###,
    SUPPORT_CALLS_LAST_3_MONTHS is ###',SUPPORT_CALLS_LAST_3_MONTHS,'###,
    NUM_COMPLAINTS_LAST_6_MONTHS is ###',NUM_COMPLAINTS_LAST_6_MONTHS,'###,
    SERVICE_DOWNTIME_LAST_30_DAYS is ###',SERVICE_DOWNTIME_LAST_30_DAYS,'###,
    AVG_INTERNET_SPEED_MBPS is ###',AVG_INTERNET_SPEED_MBPS,'###,
    RECENT_ISSUE_SUMMARY is ###',RECENT_ISSUE_SUMMARY,'###,
    
    Do not provide sentences like "The top 2 reasons why this customer is likely to churn are:",
    "Please note that .." and strictly do not start with "Based on the provided dataset.."
    Donot hallucinate. Give response based on the provided context of the data.
    """
    
    telecom_sql = session3.sql(f"""
        SELECT CUSTOMER_ID, PRED_CLASS,
            CASE 
                WHEN PRED_CLASS = 'Churn'
                THEN SNOWFLAKE.CORTEX.COMPLETE('claude-3-5-sonnet', 
                CONCAT('{prompt}', *)) 
                ELSE 'Not likely to Churn' 
            END AS SUMMARY 
        FROM TELECOM_CHURN_PREDICTION_OUT 
        LIMIT 5;
    """)
    
    df_telecom_ls = telecom_sql.collect()
    df_telecom = pd.DataFrame(df_telecom_ls)
    
    st.dataframe(df_telecom)
    
    session3.close()