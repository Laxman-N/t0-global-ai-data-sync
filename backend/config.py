from dotenv import load_dotenv
import os

load_dotenv()

# --- API Configuration ---
# Uses the environment variable API_BASE_URL, defaults to http://127.0.0.1:8000
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


# --- Snowflake Credentials Configuration (CRITICAL FIX APPLIED TO PASSWORD) ---

# Your Snowflake Username (Set to default "LAXMAN" if not in .env)
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER", "LAXMAN")

# Your Snowflake Password - MUST use "SNOWFLAKE_PASSWORD" as the variable name
# If the environment variable is not set, it defaults to your password string
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD", "Sathyaveni143#")

# Your Snowflake Account Identifier (e.g., xy12345.us-east-1)
SNOWFLAKE_ACCOUNT = os.getenv(
    "SNOWFLAKE_ACCOUNT", "GDXNPBE-ZT25716")

# Database resources (these should typically be environment variables too)
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "T0_WH")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE", "GLOBAL_HOSPITAL_DB")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "HOSPITAL_SYNC")

# Note: All redundant hardcoded variable assignments have been removed.
