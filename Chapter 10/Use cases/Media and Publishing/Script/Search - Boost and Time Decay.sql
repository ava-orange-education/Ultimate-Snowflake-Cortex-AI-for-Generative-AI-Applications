USE CORTEX_AI_DB.PUBLIC;

-- Load TECH_BOOK_CATALOG table to CORTEX_AI_DB.PUBLIC.TECH_BOOK_CATALOG

--Verify

SELECT * FROM TECH_BOOK_CATALOG;

-- Create Search Service for fast and scalable semantic search over book descriptions

CREATE OR REPLACE CORTEX SEARCH SERVICE tech_book_catalog_css
    ON book_description
    WAREHOUSE = COMPUTE_WH
    TARGET_LAG = '1 minute'
AS SELECT * FROM tech_book_catalog;
----------------------------------------------

-- Implementing the BOOST feature
-- Use SNOWFLAKE.CORTEX.SEARCH_PREVIEW to search the tech_book_catalog_css search service for content matching the keyword "AI". 
-- It applies a numeric boost to prioritize results based on engagement — giving twice the weight to the count of REVIEWS and single weight to count of LIKES
-- Flattens and extracts fields TITLE, BOOK_DESCRIPTION, LAST_MODIFIED_TIMESTAMP, LIKES, and REVIEWS from the results for display.

SELECT
    value ['TITLE'], value['BOOK_DESCRIPTION'], value['LAST_MODIFIED_TIMESTAMP'], value['LIKES'], value['REVIEWS']
FROM TABLE(FLATTEN(PARSE_JSON(SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'tech_book_catalog_css',
    '{
      "query": "AI",
      "columns": ["TITLE", "BOOK_DESCRIPTION", "LAST_MODIFIED_TIMESTAMP", "CREATED_TIMESTAMP", "LIKES", "REVIEWS"],
      "scoring_config": {
        "functions": {
          "numeric_boosts": [
            {"column": "REVIEWS", "weight": 2},
            {"column": "likes", "weight": 1}
          ]
        }
      }
    }'
))['results'] ));

---------------------------
-- Implementing the TIME DECAY feature

-- This query performs a semantic search for the term "AI" within the tech_book_catalog_css service using SNOWFLAKE.CORTEX.SEARCH_PREVIEW. It applies a time decay scoring function that prioritizes books recently updated(using LAST_MODIFIED_TIMESTAMP) within the last 200 hours, giving them a weight of 2 in the ranking. The results are flattened, and key fields such as TITLE, BOOK_DESCRIPTION, LAST_MODIFIED_TIMESTAMP, LIKES, and REVIEWS are extracted for display.

SELECT
    value['TITLE'], value['BOOK_DESCRIPTION'], value['LAST_MODIFIED_TIMESTAMP'], value['LIKES'], value['REVIEWS']
FROM TABLE(FLATTEN(PARSE_JSON(SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'tech_book_catalog_css',
    '{
      "query": "AI",
      "columns": ["TITLE", "BOOK_DESCRIPTION", "LAST_MODIFIED_TIMESTAMP", "CREATED_TIMESTAMP", "LIKES", "REVIEWS"],
      "scoring_config": {
        "functions": {
          "time_decays": [
            {"column": "LAST_MODIFIED_TIMESTAMP", "weight": 2, "limit_hours": 200}
          ]
        }
      }
    }'
))['results'] ));
------------------------
-- Boosted Book Results Vs Results without Boost - A Comparison

SELECT PARSE_JSON(SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'tech_book_catalog_css',
    '{
      "query": "AI",
      "columns": ["BOOK_DESCRIPTION", "LAST_MODIFIED_TIMESTAMP", "BOOK_DESCRIPTION", "REVIEWS", "LIKES"],
      "scoring_config" :{
        "functions": {
          "numeric_boosts": [
            {"column": "LIKES", "weight": 1}
          ]
        }
      }
    }'
))['results'] as Boosted_Book_Results,
PARSE_JSON(SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'tech_book_catalog_css',
    '{
      "query": "AI",
      "columns": ["BOOK_DESCRIPTION", "LAST_MODIFIED_TIMESTAMP", "BOOK_DESCRIPTION", "REVIEWS", "LIKES"]
    }'
))['results'] as Book_Results_without_boost;