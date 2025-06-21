-- STEP 1. Create a new stage and Load PDF documents
CREATE OR REPLACE STAGE cortex_ai_db.public.airline_stg
DIRECTORY = (ENABLE = TRUE)
ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

-- STEP 2. Create Schema
CREATE OR REPLACE SCHEMA cortex_ai_db.observability_schema;

-- STEP 3. Upload Airline documents
-- For demonstration purposes, there are two small documents
-- 1. Airline_Passenger_Experience_Guide.pdf is related to passenger experience and amenities
-- 2.Airline_Ticketing_and_Refund_Policies.pdf refers to ticketing policies
-- UPLOAD THESE TWO DOCUMENTS TO cortex_ai_db.public.airline_stg (created above)

-- STEP 4. Upload "AIRLINE_QUERIES_ANSWERS.csv" to Snowflake table (CORTEX_AI_DB.observability_schema.AIRLINE_QUERIES_ANSWERS):
-- This file contains the responses for RAG validation. We will load this to a table that will be compared with for computing the LLM's performance metrics (this experiment will be performed in the snowflake notebook)
-- The steps to upload AIRLINE_QUERIES_ANSWERS.csv to CORTEX_AI_DB.observability_schema are as follows:
-- 1. Select Data -> Add Data
-- 2. Choose the tile: Load data into a Table
-- 3. Upload `AIRLINE_QUERIES_ANSWERS.csv` from the local
-- 4. Choose `CORTEX_AI_DB.OBSERVABILITY_SCHEMA`, create a new table
-- 5. Name the new table `AIRLINE_QUERIES_ANSWERS` , then click next.
-- 6. Ensure that the option "First Line contains Headers" is selected in the Header
-- 7. Ensure the column names are `QUERY`, and `GROUND_TRUTH_RESPONSE` and select Load.

-- STEP 5: After completing the above steps, upload the notebook airline_ai_observability.ipynb to cortex_ai_db.public.

-- STEP 6: Follow the instructions in the notebook and execute the steps.





