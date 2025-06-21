-- Ensure that the set of invoices are uploaded to doc_ai_demo_stage before proceeding

-- Step - 24: Set context
USE WAREHOUSE doc_ai_demo_WH;
USE ROLE doc_ai_demo_ROLE;
USE DATABASE doc_ai_demo_DB;
USE SCHEMA doc_ai_demo_SCHEMA;

-- ## Step 25: Create a stream for the stage where the documents are uploaded
CREATE STREAM doc_ai_demo_stream ON STAGE doc_ai_demo_stage;

-- ## Step 26: Referesh the stage so that stage and stream are aligned with latest data
ALTER STAGE doc_ai_demo_stage REFRESH;

-- ## Step 27:Running Predictions on documents using the published model
SELECT doc_ai_demo_DB.doc_ai_demo_SCHEMA.ZENTIME_INVOICES!PREDICT(
GET_PRESIGNED_URL(@doc_ai_demo_stage, RELATIVE_PATH), 1) as ZenTime_Invoices_Model_Result
FROM DIRECTORY(@doc_ai_demo_stage);

-- ## Step 28: Storing the model result in a table
CREATE OR REPLACE TABLE ZENTIME_INVOICE_MODEL_RESULTS AS
SELECT doc_ai_demo_DB.doc_ai_demo_SCHEMA.ZENTIME_INVOICES!PREDICT(
GET_PRESIGNED_URL(@doc_ai_demo_STAGE, RELATIVE_PATH), 1) as Invoice_Model_Values
FROM DIRECTORY(@doc_ai_demo_STAGE);

-- ## Step 29: On reviewing the result it is seen that the output is in JSON format. It should be normalized.
SELECT * FROM ZENTIME_INVOICE_MODEL_RESULTS;

-- ## Step 30: Normalizing the results and writing to a table
CREATE OR REPLACE TABLE ZENTIME_INVOICE_MODEL_RESULTS_NORMALIZED AS
SELECT
INVOICE_MODEL_VALUES:"InvoiceNumber"[0]:value::string AS INVOICE_NUMBER,
INVOICE_MODEL_VALUES:"InvoiceDate"[0]:value::string AS INVOICE_DATE,
INVOICE_MODEL_VALUES:"Item"[0]:value::string AS ITEMS,
INVOICE_MODEL_VALUES:"PaymentMethod"[0]:value::string AS PAYMENT_METHOD,
INVOICE_MODEL_VALUES:"InvoiceTotal"[0]:value::string AS TOTAL_VALUE
FROM ZENTIME_INVOICE_MODEL_RESULTS;

-- ## Step 31: Reviewing the final results
SELECT * FROM ZENTIME_INVOICE_MODEL_RESULTS_NORMALIZED;