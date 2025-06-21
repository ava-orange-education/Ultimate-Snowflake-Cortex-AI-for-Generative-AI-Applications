USE CORTEX_AI_DB;

-- Create user_logins table that holds user id and no of logins for a day

CREATE OR REPLACE TABLE user_logins (
  user_id STRING,
  date DATE,
  failed_logins INTEGER
);

-- Load user_logins table

INSERT INTO user_logins VALUES
  ('u001', '2025-04-01', 1),
  ('u002', '2025-04-01', 4),
  ('u003', '2025-04-01', 2),
  ('u002', '2025-04-02', 5);

--  create login_threshold_config that defines the threshold for attempts in a day and insert value
  CREATE OR REPLACE TABLE login_threshold_config (
  threshold INT
);

INSERT INTO login_threshold_config VALUES (3);

--Generate code to mark as suspicious if login attempts > threshold and write to a suspicious_users table
SELECT
  SNOWFLAKE.CORTEX.COMPLETE(
    'snowflake-arctic',
    'Write Python code that reads failed login data from a Snowflake table called `user_logins`, which has columns: user_id, date, and failed_logins. Also read a threshold value from another table called `login_threshold_config`, which contains a single column `threshold`. Generate a query or logic that identifies users who had more than the threshold number of failed login attempts in a single day. write to a table called suspicious_users with columns: user_id, date, total_failed_logins, and a flag `is_suspicious` (True if failed_logins > threshold). Create this table if it is not already there.Provide the required package installations as well'
  ) AS generated_code;

-- The result provides the instructions on installation of required packages as well as the code with placeholders for substituting connection parameters etc.