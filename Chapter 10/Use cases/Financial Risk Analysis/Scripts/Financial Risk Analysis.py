# Create this application in CORTEX_AI_DB
# Import the packages from the Package List.txt into this Streamlit app (Packages -> Find Packages)
# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd

st.set_page_config(layout="wide")
    
session = get_active_session()
result = session.sql("SELECT * FROM CORTEX_AI_DB.PUBLIC.TEST_DATA_FINANCIAL_RISK")
data_list = result.collect()
df = pd.DataFrame(data_list)
# df=df.drop(columns=['RISK_FLAG'],axis=1)


c1, c2, c3 = st.columns([0.35,0.5,0.1])
with c2:
    st.header("Financial Risk Prediction")

st.write(' ')
st.write(' ')
st.subheader('Data Preview')
st.dataframe(df.head())

if st.button('Predict '):
    session3 = get_active_session()
    rs = session3.sql(""" CREATE OR REPLACE TABLE FINANCIAL_RISK_PREDICTION_OUT AS
                            SELECT * EXCLUDE prediction,
                                    prediction:class AS pred_class,
                                    round(prediction['probability'][prediction:class], 3) as probability
                            FROM FINANCIAL_RISK_PREDICTION;
                            """)
    ls = rs.collect()
    # dat_f = pd.DataFrame(ls)
    # # dat_f = dat_f.drop(columns=['TARGET_CHURN_FLAG'], axis=1)
    # st.dataframe(dat_f)

    prompt = f"""
    You are provided with a dataset containing financial risk predictions.  
    
    Analyze the attributes and provide the **top 3 significant reasons** why this customer is considered a **high financial risk**.  
    Clearly mention the column names used in your reasoning based on the list of columns below.

    **Columns:**
    ANNUAL_INCOME is ###',ANNUAL_INCOME,'###,
    DEBT_TO_INCOME_RATIO is ###',DEBT_TO_INCOME_RATIO,'###,
    CREDIT_SCORE is ###',CREDIT_SCORE,'###,
    NUM_OPEN_CREDIT_LINES is ###',NUM_OPEN_CREDIT_LINES,'###,
    LOAN_AMOUNT_REQUESTED is ###',LOAN_AMOUNT_REQUESTED,'###,
    LOAN_PURPOSE is ###',LOAN_PURPOSE,'###,
    EMPLOYMENT_STATUS is ###',EMPLOYMENT_STATUS,'###,
    BANKRUPTCY_HISTORY is ###',BANKRUPTCY_HISTORY,'###,
    LATE_PAYMENTS_LAST_YEAR is ###',LATE_PAYMENTS_LAST_YEAR,'###,
    AGE is ###',AGE,'###,
    RESIDENCE_STATUS is ###',RESIDENCE_STATUS,'###,
    EXISTING_LOANS is ###',EXISTING_LOANS,'###

    Do not provide sentences like "The top 3 reasons why this customer is likely to churn are:",
    "Please note that .." and strictly do not start with "Based on the provided dataset.."
    Donot hallucinate. Give response based on the provided context of the data.
    """

    finance_sql = session3.sql(f"""
        SELECT CUSTOMER_ID, PRED_CLASS,
            CASE 
                WHEN PRED_CLASS = 'High' 
                THEN SNOWFLAKE.CORTEX.COMPLETE('llama3-8b', CONCAT('{prompt}', *)) 
                ELSE 'Low Risk' 
            END AS SUMMARY 
        FROM FINANCIAL_RISK_PREDICTION_OUT
        LIMIT 5;
    """)

    
    df_risk_ls = finance_sql.collect()
    df_risk = pd.DataFrame(df_risk_ls)

    st.dataframe(df_risk)
    session3.close()
