CREATE STAGE CORTEX_AI_DB.PUBLIC.SAMPLE_STG  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE') DIRECTORY = ( ENABLE = true );

-- Upload the Invoice_Details.pdf to CORTEX_AI_DB.PUBLIC.SAMPLE_STG before proceeding with the Snowflake notebook. Instructions are as given below.
-- 1.   Sign in to Snowsight.
-- 2.   Select Data from the left-side navigation menu.
-- 3.   Select your database CORTEX_AI_DB and schema - "PUBLIC".
-- 4.   Select Stages and select CORTEX_AI_STG
-- 5.   From the top right, Select the + Files button.
-- 6.   Browse to choose Invoice_Details.pdf or Drag and drop the file into the UI.
-- 7.   Select Upload

