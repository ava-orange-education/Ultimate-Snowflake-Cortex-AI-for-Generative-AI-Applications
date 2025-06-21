USE DATABASE CORTEX_AI_DB;

-- Creating a Lesson Plan using COMPLETE function
SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-7b', 'Create an engaging lesson plan on photosynthesis for grade 5 students') AS Lesson_Plan;

-- Creating a Product Description using COMPLETE function
SELECT SNOWFLAKE.CORTEX.COMPLETE('claude-3-5-sonnet', 'Generate a compelling product description for a new smartphone 
                                with features like 12GB RAM, 512GB storage, and a 6.1-inch AMOLED display.') AS Product_Desc;

-- List potential new features for a smart phone using COMPLETE function
SELECT
    CUSTOMER_ID,
    CUSTOMER_FEEDBACK,
    SNOWFLAKE.CORTEX.COMPLETE(
        'claude-3-5-sonnet', -- Or any other supported LLM Model that best suits the use case
        [
            {
                'role': 'system',
                'content': 'You are a product innovation assistant. Analyze the following customer feedback and suggest potential new product features. Provide your response as a concise list of feature suggestions. Do not say here are some potential new features. Just directly list the features, without any additional text.'
            },
            {
                'role': 'user',
                'content': CUSTOMER_FEEDBACK
            }
        ],
        {
            'temperature': 0.7,
            'max_tokens': 200
        }
    ) AS FEATURE_SUGGESTIONS
FROM
    SMARTWATCH_CUSTOMER_FEEDBACK;
