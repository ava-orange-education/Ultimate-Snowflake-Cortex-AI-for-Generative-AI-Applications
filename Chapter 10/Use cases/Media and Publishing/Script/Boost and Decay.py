# Import the packages from the Package List.txt into this Streamlit app (Packages -> Find Packages)
# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import re

st.set_page_config(layout='wide')

st.markdown("""<style>
            button[data-testid="stBaseButton-secondary"] p {
                font-size: 20px;
                font-weight: 500;
            }
            button[data-testid="stBaseButton-secondary"] {
                background-color: #00008B; /* Green */
                color: white;
                padding: 8px 24px;
                border: none;
                border-radius: 24px;
                /*font-size: 50px;*/
                cursor: pointer;
                transition: background-color 0.3s ease, transform 0.2s ease;
            }
            button[data-testid="stBaseButton-secondary"]:hover {
                background-color: #80BFFF; /* Slightly darker green */
                transform: scale(1.05); /* Slight zoom effect */
            }
            /* Style when the button is clicked (active) */
            button[data-testid="stBaseButton-secondary"]:active {
                background-color: #0059B3; /* Darker green */
                transform: scale(0.98); /* Slight shrink effect */
                box-shadow: 0 5px #666; 
            }
 
</style>""", unsafe_allow_html=True)

ls = st.sidebar.radio('Options', ['Boost', 'Decay'])

if ls == 'Boost':

    session = get_active_session()

    c1, c2 = st.columns([0.35, 0.65])
    with c2:
        st.header(" Engagement-Based Boosting ")
    
    st.subheader(" Data Preview")
    
    data = session.sql(""" SELECT BOOK_ID, TITLE, BOOK_DESCRIPTION, LAST_MODIFIED_TIMESTAMP, LIKES, REVIEWS from TECH_BOOK_CATALOG;""").collect()
    df = pd.DataFrame(data)
    # df.columns = [re.search(r"\['(.*?)'\]", col).group(1) for col in df.columns]
    st.dataframe(df, hide_index=True)

    input = st.text_input('Enter Topic (To search based on book description):', '')
    
    if st.button(" Boost"):
        query = f"""
            SELECT value['BOOK_ID'], value['TITLE'],
                value['BOOK_DESCRIPTION'], value['LAST_MODIFIED_TIMESTAMP'], value['LIKES'], value['REVIEWS']
            FROM TABLE(FLATTEN(PARSE_JSON(SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                'tech_book_catalog_css',
                '{{  
                    "query": "{input}",
                    "columns": ["BOOK_ID", "TITLE", "BOOK_DESCRIPTION", "LAST_MODIFIED_TIMESTAMP", "LIKES", "REVIEWS"],
                    "scoring_config": {{
                        "functions": {{
                            "numeric_boosts": [
                                {{"column": "REVIEWS", "weight": 2}},
                                {{"column": "likes", "weight": 1}}
                            ]
                        }}
                    }}
                }}'
            ))['results']))
        """
    
        data1 = session.sql(query).collect()
        df1 = pd.DataFrame(data1)
        df1.columns = [re.search(r"\['(.*?)'\]", col).group(1) for col in df1.columns]
        st.subheader(" Top 5 Results")
        st.dataframe(df1.head(), hide_index=True)


if ls == 'Decay':
    session = get_active_session()

    c1, c2 = st.columns([0.35, 0.65])
    with c2:
        st.header(" Recency Weighting via Time Decay ")

    st.subheader(" Data Preview")
    
    data = session.sql(""" SELECT BOOK_ID, TITLE, BOOK_DESCRIPTION, LAST_MODIFIED_TIMESTAMP, LIKES, REVIEWS from TECH_BOOK_CATALOG
                    """).collect()
    df = pd.DataFrame(data)
    # df.columns = [re.search(r"\['(.*?)'\]", col).group(1) for col in df.columns]
    st.dataframe(df, hide_index=True)

    input1 = st.text_input('Enter Time Decay (Hrs):', '')
    
    if st.button(" Decay"):
        data1 = session.sql(f"""
                            SELECT value['BOOK_ID'],
                                value['TITLE'], value['BOOK_DESCRIPTION'], value['LAST_MODIFIED_TIMESTAMP'], value['LIKES'], value['REVIEWS']
                            FROM TABLE(FLATTEN(PARSE_JSON(SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                                'tech_book_catalog_css',
                                '{{  
                                    "query": "AI",
                                    "columns": ["BOOK_ID", "TITLE", "BOOK_DESCRIPTION", "LAST_MODIFIED_TIMESTAMP", "LIKES", "REVIEWS"],
                                    "scoring_config": {{
                                        "functions": {{
                                            "time_decays": [
                                                {{"column": "LAST_MODIFIED_TIMESTAMP", "weight": 2, "limit_hours": {input1}}}
                                            ]
                                        }}
                                    }}
                                }}'
                            ))['results']));
                    """).collect()
        df1 = pd.DataFrame(data1)
        df1.columns = [re.search(r"\['(.*?)'\]", col).group(1) for col in df1.columns]
        st.subheader(" Top 5 Results")
        st.dataframe(df1.head(), hide_index=True)

