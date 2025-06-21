# Create this application in CORTEX_AI_DB
# Import the packages from the Package List.txt into this Streamlit app (Packages -> Find Packages)
# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from snowflake.snowpark import exceptions
from skimage import io, transform

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



if 'report_btn' not in st.session_state:
    st.session_state.report_btn = False

def changehandler():
    st.session_state.report_btn = False

        
# Get the current credentials
session = get_active_session()

def display_in_box(message):
    st.markdown(
        f"""
        <div style="
            border: 3px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            background-color: #f9f9f9;
            box-shadow: 2px 4px 5px rgba(0, 0, 0, 0.1);
            font-size: 14px;
            font-family: Arial, sans-serif;
        ">
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )

## Fetch Databases
result_db = session.sql("select * from INFORMATION_SCHEMA.DATABASES;")
result_tab = session.sql('select * from INFORMATION_SCHEMA.TABLES')
list_db = result_db.collect()
df_db =  pd.DataFrame(list_db)
# st.write(df_db)

# Streamlit layout
c1, c2, c3 = st.columns(3)

with c1:
    # Choose Database
    databases = df_db["DATABASE_NAME"].unique()
    if len(databases) == 0:
        st.warning("Please create a database and come to this tab.")
    else:
        database = st.selectbox("Choose database", databases, on_change=changehandler)
        df_db = df_db[df_db["DATABASE_NAME"] == database]

with c2:
    if len(databases) == 0:
        # No database to select, so no need to proceed
        st.warning("Please create a database and come to this tab.")
    else:
        # Fetch Schema for the selected database
        result_sch = session.sql(f'''select * from {database}.INFORMATION_SCHEMA.SCHEMATA''')
        list_sch = result_sch.collect()
        df_sch = pd.DataFrame(list_sch)

        schemas = df_sch["SCHEMA_NAME"].unique()
        if len(schemas) == 0:
            st.warning(f"No schemas found in database '{database}'. Please create a schema.")
        else:
            # Choose Schema
            schema = st.selectbox("Choose Schema", schemas, on_change=changehandler)
            df_sch = df_sch[df_sch["SCHEMA_NAME"] == schema]

with c3:
    if len(databases) == 0 or len(schemas) == 0:
        # If no database or schema is available, no need to proceed to table selection
        st.warning("Please create a database and schema and come to this tab.")
    else:
        # Fetch Tables for the selected schema
        result_tab = session.sql(f'''select * from {database}.INFORMATION_SCHEMA.TABLES''')
        list_tab = result_tab.collect()
        df_tab = pd.DataFrame(list_tab)
        df_tab = df_tab[df_tab["TABLE_SCHEMA"] == schema]

        tables = df_tab["TABLE_NAME"].unique().tolist()
        if len(tables) == 0:
            st.warning(f"No tables found in schema '{schema}'. Please create a table.")
        else:
            # Choose Table
            table = st.selectbox("Choose Table", ['None'] + tables, on_change=changehandler)

if len(tables) != 0 and table is not 'None':
    st.subheader('Data Preview')
    ls = session.sql(f"select * from {database}.{schema}.{table};").collect()
    df = pd.DataFrame(ls)
    st.dataframe(df.head())


    if st.button("Generate Summary"):
        try:
            sql_call = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3-70b', 
                    CONCAT('Summarize the key insights from the following data (if there 
                    are any trends, observations, or anomalies, please highlight them) {df}. Provide
                    some information on key columns and associated data distributions in terms of percentage, ratio, etc. as applicable.
                    Identify key factors that play a major role. Provide data in a neatly tabulated form. 
                    Do not hallucinate about the data. Do not say sentences like "this analysis is 
                    limited to the provided data and might not be representative of the entire 
                    dataset", as the provided data is the entire dataset. Summarize or provide details for as many fields as possible and not 
                    just for a limited set of fields. Be detailed and elaborate. Provide impactful observations. 
                    Also, highlight any notable anomalies. Summarize the data as well.
                    Do not display "</div>" at the end of your response')) as SUMMARY;
            """
            
            # Execute the SQL query to get the summary
            df_summary = session.sql(sql_call).to_pandas()
        
            # Display the summary result from the first row
            display_in_box(df_summary['SUMMARY'][0])
        
        except exceptions.SnowparkSQLException as e:
            if "unknown model" in str(e) or \
                "The required LLMs for Cortex Analyst are not available in your region" in str(e):
                st.error("""
                    **To Generate Summary, ensure that Cortex LLM Functions are enabled for your region.** 
                    If Cortex LLM functions are not enabled, you could consider enabling cross-region inference by referring to the following link:
                    https://docs.snowflake.com/en/user-guide/snowflake-cortex/cross-region-inference
                    This enables inference requests to be processed from a different region where LLMs are available. **Please note that you will be charged credits for the use of LLM as described in detail in the above link. Credits are considered consumed in the requesting region.**
                """)
            else:
                st.error(f"An unexpected error occurred: {str(e)}")
                print(f"Unexpected Error: {str(e)}")


