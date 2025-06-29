USE DATABASE CORTEX_AI_DB;
 
-- Ensure that you have imported the data from Financial_Risk.csv to the FINANCIAL_RISK table

SELECT * FROM FINANCIAL_RISK;
 
--------Creating Train and Test Tables------------

CREATE OR REPLACE TABLE TRAIN_DATA_FINANCIAL_RISK AS
SELECT * FROM CORTEX_AI_DB.PUBLIC.FINANCIAL_RISK SAMPLE (80);

CREATE OR REPLACE TABLE CORTEX_AI_DB.PUBLIC.TEST_DATA_FINANCIAL_RISK 
AS
SELECT * FROM FINANCIAL_RISK WHERE NOT EXISTS (
SELECT 1 FROM TRAIN_DATA_FINANCIAL_RISK WHERE
FINANCIAL_RISK.CUSTOMER_ID = TRAIN_DATA_FINANCIAL_RISK.CUSTOMER_ID);

-- VERIFYING THE COUNT OF TRAIN AND TEST DATA AGAINST THE SOURCE TABLE
SELECT COUNT(*) FROM FINANCIAL_RISK;

SELECT COUNT(*) FROM TRAIN_DATA_FINANCIAL_RISK
union all
SELECT COUNT(*) FROM TEST_DATA_FINANCIAL_RISK;
 
------------ DROPPING UNUSED CUSTOMER_ID COLUMN FROM TRAIN AND TARGET COLUMN FROM TEST TABLE
ALTER TABLE TRAIN_DATA_FINANCIAL_RISK DROP COLUMN CUSTOMER_ID;
ALTER TABLE TEST_DATA_FINANCIAL_RISK DROP COLUMN RISK_FLAG;
 
------------------------------- NATIVE CLASSIFIER CREATION ---------------------------------
 
-- CREATION OF ML CLASSIFIER
CREATE OR REPLACE SNOWFLAKE.ML.CLASSIFICATION FINANCIAL_RISK_MODEL(
    INPUT_DATA => SYSTEM$REFERENCE('TABLE', 'TRAIN_DATA_FINANCIAL_RISK'),
    TARGET_COLNAME => 'RISK_FLAG'
);
 
-- CREATE A TABLE FOR PREDICTIONS AND STORE THE PREDICTED OUTCOME FROM TEST DATA 
CREATE OR REPLACE TABLE FINANCIAL_RISK_PREDICTION AS
SELECT *, FINANCIAL_RISK_MODEL!PREDICT(INPUT_DATA => object_construct(*))
as prediction from TEST_DATA_FINANCIAL_RISK;

-- QUERY THE PREDICTION TABLE
 
SELECT * FROM FINANCIAL_RISK_PREDICTION;
 
-- PARSE THE PREDICTED CLASS AND PROBABILITY INTO SEPERATE COLUMNS
SELECT * EXCLUDE prediction,
        prediction:class AS pred_class,
        round(prediction['probability'][prediction:class], 3) as probability
FROM FINANCIAL_RISK_PREDICTION;
 
 
-- -- INSPECT YOUR MODELS EVALUATION METRICS
CALL FINANCIAL_RISK_MODEL!SHOW_EVALUATION_METRICS();
 
-- VERIFY FEATURE IMPORTANCE  
CALL FINANCIAL_RISK_MODEL!SHOW_FEATURE_IMPORTANCE();