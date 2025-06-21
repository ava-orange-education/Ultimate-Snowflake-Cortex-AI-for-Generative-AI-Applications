-- Run these steps after creating the CORTEX_AI_DB.PUBLIC.CUST_EMAILS table using the email_content.csv file

--1. Verify data in the CUST_EMAILS table

SELECT * FROM CORTEX_AI_DB.PUBLIC.CUST_EMAILS;
 
--2. Retrieve the entity sentiments from the table and create a new table called CUSTOMER_SENTIMENT

CREATE TABLE CORTEX_AI_DB.PUBLIC.CUSTOMER_SENTIMENT AS
SELECT *,
  SNOWFLAKE.CORTEX.ENTITY_SENTIMENT(
    email_content,
    ['overall', 'Brand', 'Product', 'Service', 'Design']
  ) AS entity_sentiment_output
FROM CUST_EMAILS;

--3. Normalize down the Output to view aspect level sentiment and store in cust_entity_Sentiment table

create table CORTEX_AI_DB.PUBLIC.cust_entity_Sentiment as
WITH flattened AS (
  SELECT 
    t.*,
    f.value:name::STRING AS category,
    f.value:sentiment::STRING AS sentiment
  FROM CORTEX_AI_DB.PUBLIC.customer_sentiment t,
       LATERAL FLATTEN(input => t.entity_sentiment_output:categories) f
)
SELECT id, 
  EMAIL_CONTENT,
  MAX(CASE WHEN category = 'overall' THEN sentiment END) AS overall_sentiment,
  MAX(CASE WHEN category = 'Brand' THEN sentiment END) AS brand_sentiment,
  MAX(CASE WHEN category = 'Product' THEN sentiment END) AS product_sentiment,
  MAX(CASE WHEN category = 'Service' THEN sentiment END) AS service_sentiment,
  MAX(CASE WHEN category = 'Design' THEN sentiment END) AS design_sentiment
FROM flattened
group by id, email_content
order by id;

-- 4. Verify Results
SELECT * FROM CORTEX_AI_DB.PUBLIC.cust_entity_Sentiment;

