-- USE DATABASE
USE DATABASE CORTEX_AI_DB;

SELECT * FROM RETAIL_SALES;

-- create forecast model
CREATE OR REPLACE SNOWFLAKE.ML.FORECAST SALES_FORECAST(
    INPUT_DATA => SYSTEM$REFERENCE('TABLE', 'RETAIL_SALES'),
    TIMESTAMP_COLNAME => 'DATE',
    TARGET_COLNAME => 'SALES',
    CONFIG_OBJECT => { 'ON_ERROR': 'SKIP' }
);

-- Generate forecasted predictions and store the results to a table.
BEGIN
    -- This is the step that creates your predictions.
    CALL SALES_FORECAST!FORECAST(
        -- Here we set your prediction interval.
        FORECASTING_PERIODS => 14
    );
    -- These steps store your predictions to a table.
    LET x := SQLID;
    CREATE OR REPLACE TABLE RETAIL_SALES_FORECAST AS SELECT * FROM TABLE(RESULT_SCAN(:x));
END;

-- View forecasted sales output
SELECT * FROM RETAIL_SALES_FORECAST;