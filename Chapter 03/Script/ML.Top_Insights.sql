-- USE DATABASE
USE DATABASE CORTEX_AI_DB;

SELECT * FROM PURCHASE_INSIGHTS;

-- CREATE TOP INSIGHTS MODEL
CREATE OR REPLACE SNOWFLAKE.ML.TOP_INSIGHTS my_insights_model();

-- CALL function to get the key drivers 
CALL my_insights_model!get_drivers(
  INPUT_DATA => TABLE(PURCHASE_INSIGHTS),
  LABEL_COLNAME => 'DISCOUNT_AVAILED',
  METRIC_COLNAME => 'PURCHASE_AMOUNT'
);

-- Store the results 
CREATE OR REPLACE TABLE PURCHASE_INSIGHTS_RESULTS AS SELECT * FROM TABLE (RESULT_SCAN(-1));

SELECT * FROM PURCHASE_INSIGHTS_RESULTS;