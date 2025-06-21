----- creating a stage for document uploads
USE DATABASE CORTEX_AI_DB;
create schema HOSP_SEARCH;
create or replace stage docs ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE') DIRECTORY = ( ENABLE = true );