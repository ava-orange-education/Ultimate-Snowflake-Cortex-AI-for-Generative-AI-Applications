-- PLEASE UPDATE THE <YOUR_SNOWFLAKE_USER_ID> IN STEP 7 WITH YOUR LOGGED IN SNOWFLAKE USER ID BEFORE EXECUTING THE STEP

-- ## Step 1: Using ACCOUNTADMIN role to set up access
USE ROLE ACCOUNTADMIN;

-- ## Step 2: Create a custom role and Grant the required privileges for the role for Document AI
CREATE ROLE doc_ai_demo_role;
GRANT DATABASE ROLE SNOWFLAKE.DOCUMENT_INTELLIGENCE_CREATOR TO ROLE doc_ai_demo_role;

-- ## Step 3: Create a new database, schema, and warehouse to track Document AI usage. By default an xs warehouse is created.
CREATE DATABASE doc_ai_demo_db;
CREATE SCHEMA doc_ai_demo_db.doc_ai_demo_schema;
CREATE WAREHOUSE doc_ai_demo_wh;

-- ## Step 4: Granting Document AI Role access to these resources
GRANT USAGE, OPERATE ON WAREHOUSE doc_ai_demo_wh TO ROLE doc_ai_demo_role;
GRANT USAGE ON DATABASE doc_ai_demo_db TO ROLE doc_ai_demo_role;
GRANT USAGE ON SCHEMA doc_ai_demo_db.doc_ai_demo_schema TO ROLE doc_ai_demo_role;

-- ## Step 5: Grant the role access to create "DOCUMENT INTELLIGENCE" process in the Schema created.
GRANT CREATE SNOWFLAKE.ML.DOCUMENT_INTELLIGENCE ON SCHEMA doc_ai_demo_db.doc_ai_demo_schema TO ROLE doc_ai_demo_role;

-- ## Step 6: Grant the role to create stage, table, stream, task, view on the newly created schema.
GRANT CREATE STAGE ON SCHEMA doc_ai_demo_db.doc_ai_demo_schema TO ROLE doc_ai_demo_role;
GRANT CREATE STREAM, CREATE TABLE, CREATE TASK, CREATE VIEW ON SCHEMA doc_ai_demo_db.doc_ai_demo_schema TO ROLE doc_ai_demo_role;
GRANT EXECUTE TASK ON ACCOUNT TO ROLE doc_ai_demo_role;

-- ######## Step 7: Assign the role either to a newly created user or an existing user so that all the privileges of the role will get transferred to the user
GRANT ROLE doc_ai_demo_role TO USER <YOUR_SNOWFLAKE_USER_ID>; -- ** Replace with your userid

-- ## Step 8: Use the role that were assigned with all the above privileges.
USE ROLE doc_ai_demo_role;

-- ## Step 9: Navigate to database and schema where we will use the Document AI function
USE database doc_ai_demo_db;
USE schema doc_ai_demo_schema;

-- ## Step 10: Create a stage for uploading invoices for prediction
CREATE STAGE doc_ai_demo_stage
  DIRECTORY = (ENABLE = TRUE)
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

-- ## Step 11: Now Please move to the Document AI Interface in the AI & ML Section