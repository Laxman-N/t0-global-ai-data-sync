# ❄️ Snowflake Database Setup Guide

Complete guide for setting up and configuring Snowflake for the Global AI Data Sync Dashboard.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Snowflake Setup](#initial-snowflake-setup)
3. [Database Configuration](#database-configuration)
4. [Table Creation](#table-creation)
5. [User Permissions](#user-permissions)
6. [Connection Testing](#connection-testing)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Prerequisites

Before starting, ensure you have:

- ✅ Active Snowflake account (Trial or paid)
- ✅ Admin access to create databases and schemas
- ✅ Snowflake account identifier (format: `<account_locator>.<region>.<cloud>`)
- ✅ Valid user credentials

### Finding Your Snowflake Account Identifier

Your account identifier format depends on your Snowflake edition:

```
Format: <account_locator>.<region>.<cloud>
Example: xy12345.us-east-1.aws
```

To find it:
1. Log into Snowflake web interface
2. Look at the URL: `https://<account_identifier>.snowflakecomputing.com`
3. Your account identifier is the part before `.snowflakecomputing.com`

---

## 🚀 Initial Snowflake Setup

### Step 1: Create Database

Log into your Snowflake account and run:

```sql
-- Create the main database
CREATE DATABASE IF NOT EXISTS GLOBAL_AI_SYNC;

-- Use the database
USE DATABASE GLOBAL_AI_SYNC;
```

### Step 2: Create Schema

```sql
-- Create schema for patient treatment data
CREATE SCHEMA IF NOT EXISTS HEALTHCARE_DATA;

-- Use the schema
USE SCHEMA HEALTHCARE_DATA;
```

### Step 3: Create Warehouse

```sql
-- Create a warehouse for compute resources
CREATE WAREHOUSE IF NOT EXISTS AI_SYNC_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Warehouse for AI Data Sync operations';

-- Use the warehouse
USE WAREHOUSE AI_SYNC_WH;
```

---

## 💾 Database Configuration

### Primary Table: PATIENT_TREATMENTS

This is the main table for storing patient treatment records:

```sql
CREATE TABLE IF NOT EXISTS PATIENT_TREATMENTS (
    -- Primary Identifiers
    TREATMENT_ID VARCHAR(50) PRIMARY KEY,
    HOSPITAL_ID VARCHAR(50) NOT NULL,
    PATIENT_ID VARCHAR(50) NOT NULL,
    
    -- Treatment Information
    TREATMENT_TYPE VARCHAR(100),
    TREATMENT_NOTES VARIANT,
    
    -- Time Tracking
    LOCAL_TIMESTAMP TIMESTAMP_TZ,
    T0_UTC_TIMESTAMP TIMESTAMP_NTZ NOT NULL,
    INGESTION_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    -- Metadata
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

### Table Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `TREATMENT_ID` | VARCHAR(50) | Unique identifier for each treatment record |
| `HOSPITAL_ID` | VARCHAR(50) | Hospital location identifier |
| `PATIENT_ID` | VARCHAR(50) | Anonymized patient identifier |
| `TREATMENT_TYPE` | VARCHAR(100) | Type of medical treatment |
| `TREATMENT_NOTES` | VARIANT | JSON object with treatment details |
| `LOCAL_TIMESTAMP` | TIMESTAMP_TZ | Original timestamp with timezone |
| `T0_UTC_TIMESTAMP` | TIMESTAMP_NTZ | Normalized UTC timestamp |
| `INGESTION_TIMESTAMP` | TIMESTAMP_NTZ | When record was inserted |

---

## 🔍 Indexes and Optimization

### Create Indexes for Better Performance

```sql
-- Index on hospital and timestamp for faster queries
CREATE INDEX IF NOT EXISTS idx_hospital_timestamp 
ON PATIENT_TREATMENTS(HOSPITAL_ID, T0_UTC_TIMESTAMP);

-- Index on patient ID for quick lookups
CREATE INDEX IF NOT EXISTS idx_patient_id 
ON PATIENT_TREATMENTS(PATIENT_ID);

-- Index on treatment type for analytics
CREATE INDEX IF NOT EXISTS idx_treatment_type 
ON PATIENT_TREATMENTS(TREATMENT_TYPE);
```

---

## 🔐 User Permissions

### Create Application User

```sql
-- Create a dedicated user for the application
CREATE USER IF NOT EXISTS ai_sync_user
    PASSWORD = 'YourSecurePassword123!'
    DEFAULT_WAREHOUSE = AI_SYNC_WH
    DEFAULT_NAMESPACE = GLOBAL_AI_SYNC.HEALTHCARE_DATA
    MUST_CHANGE_PASSWORD = FALSE;
```

### Grant Necessary Permissions

```sql
-- Grant warehouse usage
GRANT USAGE ON WAREHOUSE AI_SYNC_WH TO ROLE PUBLIC;

-- Grant database access
GRANT USAGE ON DATABASE GLOBAL_AI_SYNC TO ROLE PUBLIC;

-- Grant schema access
GRANT USAGE ON SCHEMA GLOBAL_AI_SYNC.HEALTHCARE_DATA TO ROLE PUBLIC;

-- Grant table permissions
GRANT SELECT, INSERT, UPDATE ON TABLE PATIENT_TREATMENTS TO ROLE PUBLIC;

-- Grant role to user
GRANT ROLE PUBLIC TO USER ai_sync_user;
```

### Security Best Practices

For production environments, create custom roles:

```sql
-- Create custom role
CREATE ROLE IF NOT EXISTS AI_SYNC_ROLE;

-- Grant specific permissions to role
GRANT USAGE ON DATABASE GLOBAL_AI_SYNC TO ROLE AI_SYNC_ROLE;
GRANT USAGE ON SCHEMA GLOBAL_AI_SYNC.HEALTHCARE_DATA TO ROLE AI_SYNC_ROLE;
GRANT SELECT, INSERT, UPDATE ON TABLE PATIENT_TREATMENTS TO ROLE AI_SYNC_ROLE;

-- Assign role to user
GRANT ROLE AI_SYNC_ROLE TO USER ai_sync_user;
```

---

## 🧪 Sample Data Insertion

### Insert Test Records

```sql
-- Insert sample treatment records
INSERT INTO PATIENT_TREATMENTS (
    TREATMENT_ID,
    HOSPITAL_ID,
    PATIENT_ID,
    TREATMENT_TYPE,
    TREATMENT_NOTES,
    LOCAL_TIMESTAMP,
    T0_UTC_TIMESTAMP
) VALUES 
(
    'TRT_001',
    'HOSPITAL_A',
    'P_001',
    'Medication_Administration',
    PARSE_JSON('{"drug": "Aspirin", "dose": "5mg", "route": "Oral"}'),
    '2025-10-07 15:30:00 +05:30',
    '2025-10-07 10:00:00'
),
(
    'TRT_002',
    'HOSPITAL_B',
    'P_002',
    'Blood_Pressure_Check',
    PARSE_JSON('{"systolic": 120, "diastolic": 80, "unit": "mmHg"}'),
    '2025-10-07 09:15:00 -05:00',
    '2025-10-07 14:15:00'
),
(
    'TRT_003',
    'HOSPITAL_A',
    'P_003',
    'Temperature_Monitoring',
    PARSE_JSON('{"temperature": 98.6, "unit": "F", "method": "Oral"}'),
    '2025-10-07 08:00:00 +00:00',
    '2025-10-07 08:00:00'
);
```

### Verify Data Insertion

```sql
-- Check inserted records
SELECT 
    TREATMENT_ID,
    HOSPITAL_ID,
    PATIENT_ID,
    TREATMENT_TYPE,
    LOCAL_TIMESTAMP,
    T0_UTC_TIMESTAMP,
    INGESTION_TIMESTAMP
FROM PATIENT_TREATMENTS
ORDER BY INGESTION_TIMESTAMP DESC
LIMIT 10;
```

---

## 🔌 Connection Testing

### Test Basic Connectivity

```sql
-- Verify current session
SELECT CURRENT_ACCOUNT(), CURRENT_DATABASE(), CURRENT_SCHEMA();

-- Check warehouse status
SHOW WAREHOUSES LIKE 'AI_SYNC_WH';

-- Verify table exists
SHOW TABLES LIKE 'PATIENT_TREATMENTS';

-- Count records
SELECT COUNT(*) AS total_records FROM PATIENT_TREATMENTS;
```

### Python Connection Test

Create a test file `test_connection.py`:

```python
import snowflake.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

try:
    # Create connection
    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA')
    )
    
    # Create cursor
    cursor = conn.cursor()
    
    # Test query
    cursor.execute("SELECT CURRENT_TIMESTAMP()")
    result = cursor.fetchone()
    print(f"✅ Connection successful! Current time: {result[0]}")
    
    # Close connection
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Connection failed: {str(e)}")
```

Run the test:
```bash
python test_connection.py
```

---

## 🛠 Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Invalid account identifier"

**Solution:**
```bash
# Verify your account format
# Correct format: <account_locator>.<region>.<cloud>
# Example: xy12345.us-east-1.aws

# NOT: xy12345.snowflakecomputing.com
```

#### Issue 2: "Database does not exist"

**Solution:**
```sql
-- List all databases
SHOW DATABASES;

-- Verify database name matches .env file
USE DATABASE GLOBAL_AI_SYNC;
```

#### Issue 3: "Insufficient privileges"

**Solution:**
```sql
-- Check current role
SELECT CURRENT_ROLE();

-- Grant necessary permissions
GRANT USAGE ON DATABASE GLOBAL_AI_SYNC TO ROLE YOUR_ROLE;
GRANT USAGE ON SCHEMA HEALTHCARE_DATA TO ROLE YOUR_ROLE;
```

#### Issue 4: "Warehouse suspended or not available"

**Solution:**
```sql
-- Resume warehouse manually
ALTER WAREHOUSE AI_SYNC_WH RESUME;

-- Verify warehouse is running
SHOW WAREHOUSES;
```

#### Issue 5: "Connection timeout"

**Solution:**
- Check your firewall settings
- Verify network connectivity
- Ensure Snowflake account is active (trial not expired)
- Try increasing connection timeout in Python:
```python
conn = snowflake.connector.connect(
    ...,
    login_timeout=30,
    network_timeout=30
)
```

---

## 📊 Monitoring and Maintenance

### Query History

```sql
-- View recent queries
SELECT 
    QUERY_ID,
    QUERY_TEXT,
    START_TIME,
    END_TIME,
    EXECUTION_STATUS,
    TOTAL_ELAPSED_TIME
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE USER_NAME = CURRENT_USER()
ORDER BY START_TIME DESC
LIMIT 20;
```

### Table Statistics

```sql
-- Get table size and row count
SELECT 
    TABLE_CATALOG,
    TABLE_SCHEMA,
    TABLE_NAME,
    ROW_COUNT,
    BYTES,
    BYTES / (1024*1024) AS SIZE_MB
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME = 'PATIENT_TREATMENTS';
```

### Warehouse Credits Usage

```sql
-- Check warehouse usage (last 7 days)
SELECT 
    WAREHOUSE_NAME,
    SUM(CREDITS_USED) AS TOTAL_CREDITS,
    SUM(CREDITS_USED_COMPUTE) AS COMPUTE_CREDITS,
    SUM(CREDITS_USED_CLOUD_SERVICES) AS CLOUD_CREDITS
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD(DAY, -7, CURRENT_TIMESTAMP())
GROUP BY WAREHOUSE_NAME
ORDER BY TOTAL_CREDITS DESC;
```

---

## 🔄 Backup and Recovery

### Create Backup Table

```sql
-- Create backup of current data
CREATE TABLE PATIENT_TREATMENTS_BACKUP AS
SELECT * FROM PATIENT_TREATMENTS;

-- Verify backup
SELECT COUNT(*) FROM PATIENT_TREATMENTS_BACKUP;
```

### Restore from Backup

```sql
-- Restore specific records
INSERT INTO PATIENT_TREATMENTS
SELECT * FROM PATIENT_TREATMENTS_BACKUP
WHERE TREATMENT_ID NOT IN (SELECT TREATMENT_ID FROM PATIENT_TREATMENTS);
```

---

## 📝 Environment Variables Reference

Your `.env` file should contain:

```env
# Snowflake Connection Details
SNOWFLAKE_USER=ai_sync_user
SNOWFLAKE_PASSWORD=YourSecurePassword123!
SNOWFLAKE_ACCOUNT=xy12345.us-east-1.aws
SNOWFLAKE_WAREHOUSE=AI_SYNC_WH
SNOWFLAKE_DATABASE=GLOBAL_AI_SYNC
SNOWFLAKE_SCHEMA=HEALTHCARE_DATA

# Optional: Connection Settings
SNOWFLAKE_ROLE=AI_SYNC_ROLE
SNOWFLAKE_TIMEOUT=30
```

---

## 📚 Additional Resources

- [Snowflake Documentation](https://docs.snowflake.com/)
- [Python Connector Guide](https://docs.snowflake.com/en/user-guide/python-connector.html)
- [SQL Reference](https://docs.snowflake.com/en/sql-reference.html)
- [Best Practices](https://docs.snowflake.com/en/user-guide/intro-best-practices.html)

---

## ✅ Setup Checklist

- [ ] Snowflake account created and accessible
- [ ] Database `GLOBAL_AI_SYNC` created
- [ ] Schema `HEALTHCARE_DATA` created
- [ ] Warehouse `AI_SYNC_WH` created and configured
- [ ] Table `PATIENT_TREATMENTS` created
- [ ] Indexes created for performance
- [ ] User account created with proper permissions
- [ ] `.env` file configured with credentials
- [ ] Connection tested successfully
- [ ] Sample data inserted and verified

---

<div align="center">

**Need Help?** Open an issue on GitHub or contact support

[⬆ Back to Top](#️-snowflake-database-setup-guide)

</div>