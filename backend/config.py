from dotenv import load_dotenv
import os

load_dotenv()

# --- API Configuration ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# --- Snowflake Credentials (IMPORTANT: Replace placeholders or set environment variables) ---
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER", "YOUR_SNOWFLAKE_USERNAME")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD", "YOUR_SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv(
    "SNOWFLAKE_ACCOUNT", "YOUR_SNOWFLAKE_ACCOUNT_IDENTIFIER")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "T0_WH")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE", "GLOBAL_HOSPITAL_DB")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "HOSPITAL_SYNC")

# You can create a .env file in the backend directory like this:
# SNOWFLAKE_USER=myuser
# SNOWFLAKE_PASSWORD=mypass
# SNOWFLAKE_ACCOUNT=myaccount.region
# API_BASE_URL=http://127.0.0.1:8000
