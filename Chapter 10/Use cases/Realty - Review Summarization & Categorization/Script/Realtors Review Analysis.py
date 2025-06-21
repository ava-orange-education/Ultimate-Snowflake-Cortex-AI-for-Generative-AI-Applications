# Create this Streamlit application in CORTEX_AI_DB
# Import the packages from the Package List.txt into this Streamlit app (Packages -> Find Packages)
# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

st.set_page_config(layout="wide")

session = get_active_session()
# style
th_props = [
  ('font-size', '15px'),
  ('text-align', 'center'),
  ('font-weight', 'bold'),
  ('color', 'green'),
  ('background-color', '#f7ffff')
  ]
                               
td_props = [
  ('font-size', '13px'),
   ('text-align', 'center')
  ]
                                 
styles = [
  dict(selector="th", props=th_props),
  dict(selector="td", props=td_props)
  ]
    
# page layout
head_1, head_2, head_3 = st.columns([25,60, 15])
    
with head_2:
    st.markdown("## Review Summarization and Categorization")
    
df_reviews = session.table('CORTEX_AI_DB.public.Realtor_Customer_Reviews')
list = df_reviews.collect()
df = pd.DataFrame(list)

col_llm11,col_llm21,col_llm31, col_llm41 = st.columns([65, 2, 30, 3]) 

with col_llm11:
    df_tab = df[['REVIEW']].head(20)
    df_result = df_tab
    df_result=df_result.style.set_properties(**{'text-align': 'center'}).set_table_styles(styles)
    st.table(df_result)
    
prompt_category = """You are an agent that helps to handle housing customers reviews based on their experinece with realtors.

The reviews typically fall into several categories that cover various aspects of their experience.These categories include both complaints and praise:

These are the only types of review categories. So, limit the responses strictly to these categories only

Agent Support
Services
Property Related
Process Related
Pricing

Remember there should be only one category for each review.
Give strictly only the category and no other sentences or words.
Avoid mentioning sentences such as "Here is the review category:" and return the category only.
"""
prompt_summary ="""You are an agent that helps to summarize the input data. Strictly summarize them within 12 words.
"""

if st.button("Summarize & Categorize"):
    llama3_8b_response_sql = f"""CREATE OR REPLACE TABLE CORTEX_AI_DB.public.Realtor_Customer_Results AS select
    trim(snowflake.cortex.complete('llama3-8b',concat('{prompt_category}',REVIEW)),'\n') as REVIEW_CATEGORY,
    trim(snowflake.cortex.complete('llama3-8b',concat('{prompt_summary}',REVIEW)),'\n') as SUMMARY
    from CORTEX_AI_DB.public.Realtor_Customer_Reviews"""
    
    df_llama3_8b_response = session.sql(llama3_8b_response_sql)
    res = df_llama3_8b_response.collect()

    table_name = session.table("CORTEX_AI_DB.public.Realtor_Customer_Results")
    llama_list = table_name.collect()
    llama_out = pd.DataFrame(llama_list)
    # st.dataframe(llama_out.head())

    c11, c21 = st.columns([0.99, 0.01])
    with c11:
        df_result = llama_out
        df_result=df_result.style.set_properties(**{'text-align': 'center'}).set_table_styles(styles)
        st.table(df_result)
       
      
session.close()