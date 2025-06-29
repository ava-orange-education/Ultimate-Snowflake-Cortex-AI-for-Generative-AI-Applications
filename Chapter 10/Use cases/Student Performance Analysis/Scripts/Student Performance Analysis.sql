-- Please execute the code below and then load the datasets, before creating the Streamlit app

-- Create Stage
CREATE STAGE CORTEX_AI_DB.PUBLIC.STUDENT_STG
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

-- CSV Format
CREATE OR REPLACE FILE FORMAT my_csv_format 
TYPE = 'CSV' 
FIELD_OPTIONALLY_ENCLOSED_BY = '"' 
SKIP_HEADER = 1;

-- CREATE STUDENT_ANSWERS TABLE 
create or replace TABLE CORTEX_AI_DB.PUBLIC.STUDENT_ANSWERS (
	ROLL_NUMBER VARCHAR(16777216),
	NAME VARCHAR(16777216),
	QUESTION_NUMBER NUMBER(38,0),
	SELECTED_OPTION VARCHAR(16777216),
	CATEGORY VARCHAR(16777216)
);