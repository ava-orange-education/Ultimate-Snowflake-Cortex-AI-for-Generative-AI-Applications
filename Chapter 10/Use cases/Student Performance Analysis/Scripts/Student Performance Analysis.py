# Create this application in CORTEX_AI_DB
# Import the packages from the Package List.txt into this Streamlit app (Packages -> Find Packages)

import streamlit as st    
import pandas as pd
import numpy as np
from snowflake.snowpark.context import get_active_session

st.set_page_config(layout="wide")

## Button Styling
st.markdown("""<style>
            button[kind="secondary"] {
                background-color: #00008B; /* Green */
                color: white;
                padding: 8px 18px;
                border: none;
                border-radius: 24px;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s ease, transform 0.2s ease;
            }
            button[kind="secondary"]:hover {
                background-color: #80BFFF; /* Slightly darker green */
                transform: scale(1.05); /* Slight zoom effect */
            }
            /* Style when the button is clicked (active) */
            button[kind="secondary"]:active {
                background-color: #0059B3; /* Darker green */
                transform: scale(0.98); /* Slight shrink effect */
                box-shadow: 0 5px #666; 
            }

            .st-emotion-cache-qcqlej.ea3mdgi1 {
                display: none;
            }

</style>""", unsafe_allow_html=True)


# Snowpark session (automatically available in Snowflake Streamlit)
session = get_active_session()

# Snowflake stage and table
STAGE_NAME = "STUDENT_STG"
TABLE_NAME = "STUDENT_ANSWERS"
FILE_FORMAT_NAME = "my_csv_format"

# Calculating length of stage to load all the files from stage to table
stage_len = session.sql("ls @STUDENT_STG").collect()
lst = pd.DataFrame(stage_len)

# List of CSV file names
csv_files = [f"Answer_Sheet_{i}.csv" for i in range(1, len(lst['name']) + 1)]

# Title
st.title("Student Performance Analysis")

# Button to load files to table
if st.button("Load all marksheets into Snowflake Table"):
    for file_name in csv_files:
        file_path = f"@{STAGE_NAME}/{file_name}"
        
        # COPY INTO query for each file
        copy_query = f"""
        COPY INTO {TABLE_NAME}
        FROM {file_path}
        FILE_FORMAT = (FORMAT_NAME = '{FILE_FORMAT_NAME}');
        """
        
        session.sql(copy_query).collect()  # Execute the query
        st.write(f"Loaded: {file_name}")

    st.success("All files uploaded successfully!")

table_check = session.sql("""
    SELECT COUNT(*) AS COUNT FROM STUDENT_ANSWERS""").collect()

if table_check[0]['COUNT'] == 0:
    st.info("Please load all marksheets from stage into Snowflake table by clicking the above button.")
else:
    
    # Collect the Student Answers to match against the Master Answers.
    ls = session.sql("SELECT * FROM STUDENT_ANSWERS;").collect()
    df = pd.DataFrame(ls)
    
    if not df.empty:
        student_names = df['NAME'].unique().tolist()
    
    # Collecting master table
    master = session.sql("SELECT * FROM MASTER_ANSWER_KEY").collect()
    df_master = pd.DataFrame(master)
    df_master['QUESTION'] = df_master['QUESTION'].replace("'", "")
    
    # Student selection dropdown
    selected_student = st.selectbox("Select a Student:", student_names)
    
    if st.button("Calculate Marks and Generate Performace Feedback"):
        # Filter data for the selected student
        student_df = df[df['NAME'] == selected_student].copy()
        # st.dataframe(student_df)
        
        student_df = student_df.reset_index(drop=True)
        df_master = df_master.reset_index(drop=True)
        
        student_df['QUESTION'] = df_master['QUESTION']
        student_df['CORRECT_ANSWER'] =  df_master['CORRECT_ANSWER']
        
        # Create a new column 'MARK' based on the correctness of the selected option
        student_df['MARK'] = ((student_df['QUESTION_NUMBER'] == df_master['QUESTION_NUMBER']) &  
                              (student_df['SELECTED_OPTION'] == df_master['CORRECT_ANSWER'])).astype(int)
    
        # Calculate the percentage of correct MARKs
        total_questions = len(student_df)  # Total questions attempted by the student
        correct_marks = student_df['MARK'].sum()  # Total correct MARKs
        percentage = (correct_marks / total_questions) * 100 if total_questions > 0 else 0  # Avoid division by zero
        percentage = round(percentage)
        # Add percentage as a new column (same value for all rows)
        student_df['PERCENTAGE'] = percentage
    
        # Select required columns
        df1 = student_df[['CATEGORY', 'QUESTION', 'CORRECT_ANSWER', 'SELECTED_OPTION', 'MARK']]
    
        # Display the DataFrame
        st.dataframe(df1, hide_index=True)
    
        if percentage > 40:
            st.write(f" ##### {selected_student} has passed the test with {percentage}%")
        else:
            st.write(f" ##### {selected_student} has failed the test with {percentage}%")
        
        prompt = f"""
        You are an AI agent analyzing quiz performance for the student.
        
        The student attempted a multiple-choice quiz, and the questions, marks, and percentage are stored in a dataset {df1}.
        
        **Tasks:**
        1. Provide a **AI-driven feedback report**, including:
           - **Strengths**: Topics that study performed well in. 
           **If the student scored 0 or 1 or 2 in Physics or Chemistry or Mathematics or Technology or General Aptitude, strictly, do not include the respective subjects as strengths.**
           - **Ares for Improvement**: Areas where improvement is needed. Do not give response in bullet form
           - **Personalized study recommendations for {selected_student}**.
           - Provide headers in response as bold.
    
        
        Use only dataset-related context {df1} for insights and avoid unrelated information.
        """
    
    
        
        # Use the prompt in the SQL query
        query = f"""
        SELECT TRIM(SNOWFLAKE.CORTEX.COMPLETE(
            'claude-3-5-sonnet', '{prompt.replace("'", "''")}'
        ), '\n') AS Summarized_info
        """
    
        # Execute the query
        df_result = session.sql(query).to_pandas()
        
        # Display results
        st.write(df_result['SUMMARIZED_INFO'][0])
    
    session.close()
