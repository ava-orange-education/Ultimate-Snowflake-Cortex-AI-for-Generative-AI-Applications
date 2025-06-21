# Create this Streamlit application in CORTEX_AI_DB.HOSP_SEARCH
# Import the packages from the Package List.txt into this Streamlit app (Packages -> Find Packages)
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.cortex import Complete
from snowflake.core import Root
import pandas as pd
import json

st.set_page_config(layout="wide")

pd.set_option("max_colwidth", None)

# Initialize Snowflake session
session = get_active_session()
root = Root(session)

# Set the Snowflake Cortex Search Service Parameters
CORTEX_SEARCH_DATABASE = "CORTEX_AI_DB"
CORTEX_SEARCH_SCHEMA = "HOSP_SEARCH"
CORTEX_SEARCH_SERVICE = "HEALTHCARE_SEARCH_SERVICE"

# Assign the search service
svc = root.databases[CORTEX_SEARCH_DATABASE].schemas[CORTEX_SEARCH_SCHEMA].cortex_search_services[CORTEX_SEARCH_SERVICE]

# Constants
NUM_CHUNKS = 16 # You could modify this to see  how it impacts the response accuracy

# Session State Initialization
def init_messages():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []  # Ensuring messages is always initialized

    if "clear_conversation" not in st.session_state:
        st.session_state["clear_conversation"] = False

# Function to configure LLM and use the docs_chunk_table for the category
def config_options():
    st.session_state["model_name"] = "mistral-7b"

    categories = session.table('docs_chunks_table').select('category').distinct().collect()
    cat_list = ['ALL'] + [cat.CATEGORY for cat in categories]

    st.selectbox('**Select category:**', cat_list, key="category_value")


# Function to retrieve similar document chunks
def get_similar_chunks_search_service(query):
    if st.session_state.category_value == "ALL":
        response = svc.search(query, ["chunk", "relative_path", "category"], limit=NUM_CHUNKS)
    else:
        filter_obj = {"@eq": {"category": st.session_state.category_value}}
        response = svc.search(query, ["chunk", "relative_path", "category"], filter=filter_obj, limit=NUM_CHUNKS)

    return response.json()


# Engineer a prompt with retrieved documents
def create_prompt(myquestion):

    prompt_context = get_similar_chunks_search_service(myquestion)

    prompt = f"""
           You are an agent support assistant for a leading Hospital and is an expert in extracting information from the CONTEXT provided
           between <context> and </context> tags.
           When answering the question contained between <question> and </question> tags,
           be concise and do not hallucinate. 
           If you don’t have the information, just say so.

           Do not mention the CONTEXT used in your answer.

           Only answer the question if you can extract it from the CONTEXT provided.

           <context>          
           {prompt_context}
           </context>
           <question>  
           {myquestion}
           </question>
           Answer: 
    """

    json_data = json.loads(prompt_context)
    relative_paths = set(item['relative_path'] for item in json_data['results'])

    return prompt, relative_paths

# Function to generate model response
def answer_question(myquestion):
    prompt, relative_paths = create_prompt(myquestion)

    response = Complete(st.session_state.model_name, prompt)

    return response.replace("'", ""), relative_paths

# Streamlit app main function
def main():
    c1, c2 = st.columns([0.27, 0.73])
    with c2:
        st.title("Hospital Support Assistant for Staff")

    st.write('')
    st.write('')
    
    # Ensure session state is initialized
    init_messages()

    config_options()

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if question := st.chat_input("What do you want to know about your products?"):
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            question = question.replace("'", "")
            with st.spinner(f"{st.session_state.model_name} thinking..."):
                response, relative_paths = answer_question(question)
                message_placeholder.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
