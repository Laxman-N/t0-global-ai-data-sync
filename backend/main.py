import snowflake.connector
import os
import json
from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

# Use python-dotenv to load environment variables from the .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("WARNING: python-dotenv not found. Install with 'pip install python-dotenv'.")

# --- 1. Pydantic Model for Inbound Data ---


class PatientData(BaseModel):
    """Schema for the data received from the frontend to be uploaded."""
    hospital_id: str
    patient_id: str
    local_timestamp: str  # Format: YYYY-MM-DD HH:MM:SS
    treatment_type: str
    treatment_notes: Union[dict, None] = None


# --- 2. Connection Initialization (Using Password Auth) ---

SF_USER = os.getenv('SNOWFLAKE_USER')
SF_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SF_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SF_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')
SF_DATABASE = os.getenv('SNOWFLAKE_DATABASE')
SF_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA')

# Global variable to hold the connection instance
SNOWFLAKE_CONN = None


def create_snowflake_connection():
    """Establishes and returns a Snowflake connection using Username/Password."""
    global SNOWFLAKE_CONN

    if not all([SF_USER, SF_PASSWORD, SF_ACCOUNT, SF_WAREHOUSE, SF_DATABASE, SF_SCHEMA]):
        print(
            "FATAL: Missing required Snowflake environment variables. Check your .env file.")
        return None

    try:
        conn = snowflake.connector.connect(
            user=SF_USER,
            password=SF_PASSWORD,
            account=SF_ACCOUNT,
            warehouse=SF_WAREHOUSE,
            database=SF_DATABASE,
            schema=SF_SCHEMA
        )
        print("INFO: Successfully connected to Snowflake using Username/Password.")
        SNOWFLAKE_CONN = conn
        return conn

    except Exception as e:
        print(f"General Connection Error: {e}")
        SNOWFLAKE_CONN = None
        return None


# FastAPI app initialization
app = FastAPI()

# --- ADD CORS MIDDLEWARE HERE ---
app.add_middleware(
    CORSMiddleware,
    # In production, replace with specific origins like ["http://localhost:3000"]
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Perform the initial connection attempt on startup
print("INFO: Attempting initial Snowflake connection...")
SNOWFLAKE_CONN = create_snowflake_connection()


# --- 3. API Endpoints ---

@app.get("/report/summary")
async def get_report_summary():
    """
    Fetches a simple connection test from Snowflake.
    """
    global SNOWFLAKE_CONN

    if SNOWFLAKE_CONN is None:
        raise HTTPException(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable: Failed to establish Snowflake connection."
        )

    try:
        cursor = SNOWFLAKE_CONN.cursor()

        # Simple query to confirm connection and context
        query = f"SELECT CURRENT_TIMESTAMP() AS current_time, '{SF_DATABASE}.{SF_SCHEMA}' AS connected_to;"

        cursor.execute(query)
        result = cursor.fetchone()

        if not result:
            return {"message": "Query ran, but no data was returned."}

        return {
            "status": "Success",
            "message": "Connection and query executed successfully.",
            "current_db_time": str(result[0]),
            "connected_schema": result[1]
        }

    except Exception as e:
        print(f"General Error during request: {e}")
        # Try to reconnect if a transient error occurred
        SNOWFLAKE_CONN = create_snowflake_connection()
        raise HTTPException(status_code=500, detail="Internal server error.")


@app.post("/data/upload")
async def upload_patient_data(data: PatientData):
    """
    Receives patient data and inserts it into the Snowflake table.
    """
    global SNOWFLAKE_CONN

    if SNOWFLAKE_CONN is None:
        raise HTTPException(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable: Database connection is down."
        )

    try:
        cursor = SNOWFLAKE_CONN.cursor()

        # Table name must be EXACTLY PATIENT_TREATMENT_RECORDS
        # Convert treatment_notes to JSON string
        treatment_notes_json = json.dumps(
            data.treatment_notes) if data.treatment_notes else None

        # Use INSERT INTO ... SELECT syntax to allow PARSE_JSON function
        insert_query = """
        INSERT INTO PATIENT_TREATMENT_RECORDS 
        (HOSPITAL_ID, PATIENT_ID, LOCAL_TIMESTAMP, TREATMENT_TYPE, TREATMENT_NOTES, UPLOAD_TIMESTAMP)
        SELECT %s, %s, %s, %s, PARSE_JSON(%s), CURRENT_TIMESTAMP()
        """

        values = (
            data.hospital_id,
            data.patient_id,
            data.local_timestamp,
            data.treatment_type,
            treatment_notes_json
        )

        cursor.execute(insert_query, values)
        # Commit the transaction to save the data
        SNOWFLAKE_CONN.commit()

        return {
            "status": "Data Uploaded",
            "message": "Patient record successfully uploaded to Snowflake.",
            "inserted_record": data.dict()
        }

    except snowflake.connector.errors.ProgrammingError as e:
        # This will catch the 'Object does not exist or not authorized' error
        print(f"Snowflake SQL Error: {e}")
        print("\n!!! ACTION REQUIRED: The table 'PATIENT_TREATMENT_RECORDS' likely does not exist in the current schema. !!!")
        raise HTTPException(
            status_code=400, detail=f"Database insertion failed (check table/schema/query): {e}")
    except Exception as e:
        print(f"General Upload Error: {e}")
        # Try to reconnect if a transient error occurred
        SNOWFLAKE_CONN = create_snowflake_connection()
        raise HTTPException(
            status_code=500, detail="Internal server error during upload.")
