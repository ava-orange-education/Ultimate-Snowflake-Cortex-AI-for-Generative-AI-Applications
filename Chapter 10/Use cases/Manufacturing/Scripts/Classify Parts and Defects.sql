USE DATABASE CORTEX_AI_DB;
-- Step 1: Stage Creation - Let us create a stage for storing images of the parts
CREATE STAGE CORTEX_AI_DB.PUBLIC.PARTS_STAGE ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE') DIRECTORY = (ENABLE = True);

-- Step 2: Upload Images - Please ensure that you have loaded all the Parts images from the dataset folder to this stage (PARTS_STAGE) before proceeding.

-- Step 3: Query the Stage
SELECT * FROM DIRECTORY (@PARTS_STAGE);
-- This would return a row for each of the Parts Images that were uploaded to stage

-- Step  4: The TO_FILE function
SELECT RELATIVE_PATH, TO_FILE(FILE_URL) FROM DIRECTORY (@PARTS_STAGE);--
-- Look at any specific row returned by the above query that leverages TO_FILE. 
-- It returns very useful information such as the type of file (CONTENT_TYPE), along with other metadata such as last modified timestamp, size of file etc

-- We will now create a table with this unstructured column by leveraging the file type

-- Step 5: Create tables
create or replace TABLE PARTS_TABLE (FILE_NAME VARCHAR, EXTRACTION_DTTM TIMESTAMP_TZ(3), PARTS_IMAGE FILE);
create or replace TABLE CORTEX_AI_DB.PUBLIC.PARTS_STATUS_CLASSIFICATION (
	FILE_NAME VARCHAR(16777216),
	EXTRACTION_DTTM TIMESTAMP_TZ(3),
	PART_TYPE VARCHAR(16777216),
	PART_STATUS VARCHAR(16777216),
	DEFECT_SUMMARY VARCHAR(16777216)
);

create or replace TABLE CORTEX_AI_DB.PUBLIC.PARTS_FOR_ESCALATION (
	FILE_NAME VARCHAR(16777216),
	EXTRACTION_DTTM TIMESTAMP_TZ(3),
	PART_TYPE VARCHAR(16777216),
	PART_STATUS VARCHAR(16777216),
	DEFECT_SUMMARY VARCHAR(16777216)
);

-- Let us insert rows into this table corresponding to the Parts Images that we uploadedd

-- Step 6: Populate the PARTS_TABLE
INSERT INTO CORTEX_AI_DB.PUBLIC.PARTS_TABLE SELECT RELATIVE_PATH, LAST_MODIFIED, TO_FILE(FILE_URL) FROM DIRECTORY (@PARTS_STAGE);

-- Query the table
SELECT * FROM PARTS_TABLE;

-- Step 7: Classify Parts and Detect Defects
-- Now let us use this in a CORTEX COMPLETE function to classify the part name along with whether it is defective and a short summary of the defect

INSERT INTO CORTEX_AI_DB.PUBLIC.PARTS_STATUS_CLASSIFICATION 
(SELECT FILE_NAME, EXTRACTION_DTTM, SNOWFLAKE.CORTEX.COMPLETE('Claude-3-5-sonnet', 'Classify the part name in one or two words. Ignore any defect present in the part and just name it based on its identity.',PARTS_IMAGE ) AS part_type,
SNOWFLAKE.CORTEX.COMPLETE('Claude-3-5-sonnet', 'In exactly one word mention if the part is Good or Defective',PARTS_IMAGE ) AS part_status,
CASE WHEN part_status ='Defective'THEN SNOWFLAKE.CORTEX.COMPLETE('Claude-3-5-sonnet', 'In ten words or less summarize the defect', PARTS_IMAGE) ELSE 'No Defect' END Defect_Summary
FROM parts_table P
WHERE NOT EXISTS (SELECT 1 FROM PARTS_STATUS_CLASSIFICATION PS WHERE PS.FILE_NAME  = P.FILE_NAME));

-- Query the table and review the results

select * from CORTEX_AI_DB.PUBLIC.PARTS_STATUS_CLASSIFICATION;

-- Now Create the Streamlit application

