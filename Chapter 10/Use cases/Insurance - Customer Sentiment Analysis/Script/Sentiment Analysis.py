# Create this Streamlit application in CORTEX_AI_DB
# Import the packages from the Package List.txt into this Streamlit app (Packages -> Find Packages)
# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

c1, c2, c3 = st.columns([0.3, 0.7, 0.1])
with c2:
    st.write(" ## Sentiment Prediction")

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
    
df_reviews = session.sql('select * from INSURANCE_CUSTOMER_REVIEWS')
list = df_reviews.collect()
df = pd.DataFrame(list)
# rev_df = df['REVIEW']
# st.write(rev_df)
# st.write(df.shape)

col_llm1,col_llm2,col_llm3, col_llm4 = st.columns([99, 0.3, 0.3, 0.3]) 

with col_llm1:
    df_tab = df[['REVIEW_TEXT']]
    # Display a static table
    df_tab=df_tab.style.set_properties(**{'text-align': 'center'}).set_table_styles(styles)
    st.table(df_tab)

if st.button('Predict Sentiment'):
    sql = session.sql("""CREATE OR REPLACE TABLE INSURANCE_CUSTOMER_SENTIMENT AS
            SELECT SNOWFLAKE.CORTEX.SENTIMENT(REVIEW_TEXT) AS SCORE, REVIEW_TEXT as REVIEW FROM CORTEX_AI_DB.PUBLIC.INSURANCE_CUSTOMER_REVIEWS;
            """)
    sq1_out = sql.collect()

    sql1 = session.sql("""SELECT REVIEW, SCORE, 
                        CASE
                        WHEN SCORE > 0.5 THEN 'POSITIVE'
                        WHEN SCORE < -0.5 THEN 'NEGATIVE'
                        ELSE 'NEUTRAL' 
                        END AS SENTIMENT
                        FROM INSURANCE_CUSTOMER_SENTIMENT;""")
    sql_out1 = sql1.collect()
    list_out = pd.DataFrame(sql_out1)
    # st.dataframe(list_out)

    c1, c2 = st.columns([0.99, 0.01])
    with c1:
        df_tab1 = list_out
        df_tab1=df_tab1.style.set_properties(**{'text-align': 'center'}).set_table_styles(styles)
        st.table(df_tab1)


    # Occurrences of each Sentiment
    category_counts = list_out['SENTIMENT'].value_counts().reset_index()
    category_counts.columns = ['SENTIMENT', 'COUNT']
    
    # Create bar chart
    fig = px.bar(category_counts, x='SENTIMENT', y='COUNT', title="Sentiment Distribution", 
                 labels={'SENTIMENT': 'SENTIMENT', 'COUNT': 'COUNT'}, 
                 color_discrete_sequence=px.colors.qualitative.Set2,
                 color = 'SENTIMENT', text='COUNT')
    
    # Show the chart
    st.plotly_chart(fig)
