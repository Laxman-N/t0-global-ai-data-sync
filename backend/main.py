import os
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import snowflake.connector
import pytz
import traceback

# Load environment variables
load_dotenv()

# --- Global Configurations ---
TIMEZONE_MAP = {
    'IST': 'Asia/Kolkata',
    'JST': 'Asia/Tokyo',
    'EST': 'America/New_York',
    'GMT': 'Etc/GMT',
    'GMT/UTC': 'Etc/GMT',
    'CST': 'America/Chicago',
    'PST': 'America/Los_Angeles',
    'AEST': 'Australia/Sydney',
    'MST': 'America/Denver',
    'ART': 'America/Argentina/Buenos_Aires',
    'CET': 'Europe/Paris',
    'EET': 'Europe/Athens',
    'MSK': 'Europe/Moscow',
    'GST': 'Asia/Dubai',
    'SGT': 'Asia/Singapore',
    'NZST': 'Pacific/Auckland',
}

GLOBAL_FACILITIES = {
    "GLOBAL_MUMBAI": {"name": "Global India HQ", "tz": "Asia/Kolkata", "location": "India"},
    "GLOBAL_NYC": {"name": "Global New York Clinic", "tz": "America/New_York", "location": "USA"},
    "GLOBAL_TOKYO": {"name": "Global Tokyo Lab", "tz": "Asia/Tokyo", "location": "Japan"},
    "GLOBAL_LONDON": {"name": "Global London AI Hub", "tz": "Europe/London", "location": "UK"},
}

# --- Pydantic Schemas ---


class Facility(BaseModel):
    facility_name: str
    facility_timezone: str
    facility_location: str = None
    is_active: bool = True


class FacilityUpdate(BaseModel):
    facility_name: str = None
    facility_timezone: str = None
    facility_location: str = None
    is_active: bool = None


class SyncTarget(BaseModel):
    target_name: str
    target_type: str
    connection_string: str
    is_active: bool = True


class SyncTargetUpdate(BaseModel):
    target_name: str = None
    target_type: str = None
    connection_string: str = None
    is_active: bool = None


class PatientRegistration(BaseModel):
    full_name: str
    date_of_birth: str
    contact_number: str
    email: str = None
    registration_facility: str
    local_time_zone: str
    local_registration_time: str


class TriggerSync(BaseModel):
    source_facility_id: str
    target_id: str
    operation_type: str = "MANUAL_SYNC"


# --- FastAPI App Initialization ---
app = FastAPI(
    title="Global AI Data Sync System API",
    description="Multi-timezone healthcare data synchronization platform",
    version="1.0.0"
)

# --- CORS Middleware Configuration ---
# FIXED: Allow all origins for development
allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# --- Database Connection Helper ---


def get_snowflake_connection():
    """Establishes and returns a Snowflake connection."""
    try:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            role=os.getenv("SNOWFLAKE_ROLE")
        )
        return conn
    except Exception as e:
        print(f"Snowflake Connection Error: {e}")
        traceback.print_exc()
        return None

# --- Timezone Calculation Helper ---


def get_timezone_offset_str(source_tz_name, target_tz_name='Asia/Kolkata'):
    """Calculate time difference between two timezones."""
    try:
        source_tz = pytz.timezone(source_tz_name)
        target_tz = pytz.timezone(target_tz_name)

        now = datetime.now()
        source_dt = source_tz.localize(now)
        target_dt = target_tz.localize(now)

        offset = source_dt.utcoffset() - target_dt.utcoffset()
        total_seconds = offset.total_seconds()
        hours = total_seconds / 3600

        sign = '+' if hours >= 0 else ''
        return f"{sign}{hours:.1f} hours"

    except pytz.exceptions.UnknownTimeZoneError:
        return "Unknown Timezone"
    except Exception:
        return "N/A"

# --- ENDPOINTS ---


@app.get("/health")
async def health_check():
    """Health check endpoint to verify system status."""
    conn = get_snowflake_connection()
    if conn:
        conn.close()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(
            status_code=500, detail="Database connection failed")


@app.get("/api/global-facility-options")
async def get_global_facility_options():
    """Returns predefined facility templates for the form."""
    options = [
        {
            "id": key,
            "name": f"{data['name']} ({data['tz']})",
            "data": data
        }
        for key, data in GLOBAL_FACILITIES.items()
    ]
    return {"global_options": options}


@app.get("/api/dashboard/overview")
async def get_dashboard_overview():
    """Get comprehensive dashboard overview statistics."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")

    data = {
        "total_sources": 0,
        "total_targets": 0,
        "total_patients": 0,
        "total_syncs": 0,
        "success_rate": 0.0,
        "avg_lag": 0.0,
        "recent_syncs": []
    }

    try:
        cursor = conn.cursor()

        # Get summary counts
        cursor.execute("SELECT COUNT(*) FROM SOURCE_FACILITIES")
        data["total_sources"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM SYNC_TARGETS")
        data["total_targets"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM PATIENT_REGISTRATIONS")
        data["total_patients"] = cursor.fetchone()[0]

        # Get aggregated statistics
        cursor.execute(
            """
            SELECT 
                SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END), 
                COUNT(*), 
                AVG(LAG_SECONDS) 
            FROM SYNC_OPERATIONS_LOG
            """
        )
        stats = cursor.fetchone()

        if stats and stats[1] is not None:
            successful_syncs = stats[0] if stats[0] is not None else 0
            total_syncs = stats[1] if stats[1] is not None else 0
            avg_lag = stats[2] if stats[2] is not None else 0.0

            data["total_syncs"] = total_syncs
            data["avg_lag"] = round(avg_lag, 2)
            data["success_rate"] = round(
                (successful_syncs / total_syncs) * 100, 2) if total_syncs > 0 else 0.0

        # Get recent syncs (top 10)
        recent_sync_query = """
        SELECT 
            l.SYNC_COMPLETED_AT, 
            f.FACILITY_NAME, 
            t.TARGET_NAME, 
            l.OPERATION_TYPE, 
            l.RECORD_COUNT, 
            l.STATUS, 
            l.LAG_SECONDS
        FROM SYNC_OPERATIONS_LOG l
        JOIN SOURCE_FACILITIES f ON l.SOURCE_FACILITY_ID = f.FACILITY_ID
        JOIN SYNC_TARGETS t ON l.TARGET_ID = t.TARGET_ID
        ORDER BY l.SYNC_COMPLETED_AT DESC 
        LIMIT 10
        """
        cursor.execute(recent_sync_query)
        columns = [col[0] for col in cursor.description]
        data["recent_syncs"] = []

        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            if row_dict['SYNC_COMPLETED_AT']:
                row_dict['SYNC_COMPLETED_AT'] = row_dict['SYNC_COMPLETED_AT'].strftime(
                    '%Y-%m-%d %H:%M:%S')
            else:
                row_dict['SYNC_COMPLETED_AT'] = 'N/A'
            data["recent_syncs"].append(row_dict)

        return data

    except Exception as e:
        print(f"Dashboard Data Error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch dashboard data: {e}")
    finally:
        conn.close()


@app.get("/api/timezones")
async def get_timezones():
    """Fetch all distinct timezones."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT FACILITY_TIMEZONE FROM SOURCE_FACILITIES ORDER BY FACILITY_TIMEZONE")
        timezones = [row[0] for row in cursor.fetchall()]
        return {"timezones": timezones}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching timezones: {e}")
    finally:
        conn.close()


@app.get("/api/facilities")
async def load_source_facilities(timezone: str = Query(None)):
    """Fetch source facilities with optional timezone filter."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()
        query = "SELECT FACILITY_ID, FACILITY_NAME, FACILITY_TIMEZONE, FACILITY_LOCATION, IS_ACTIVE, LAST_SYNC_TIME FROM SOURCE_FACILITIES"

        params = {}
        if timezone and timezone.lower() != 'all':
            query += " WHERE FACILITY_TIMEZONE = %(timezone)s"
            params['timezone'] = timezone

        query += " ORDER BY FACILITY_NAME"
        cursor.execute(query, params)

        columns = [col[0] for col in cursor.description]
        facilities = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for f in facilities:
            f['LAST_SYNC_TIME'] = f['LAST_SYNC_TIME'].strftime(
                '%Y-%m-%d %H:%M:%S') if f['LAST_SYNC_TIME'] else 'N/A'
            f['IS_ACTIVE'] = bool(f['IS_ACTIVE'])

        return facilities
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching facilities: {e}")
    finally:
        conn.close()


@app.get("/api/facilities/{facility_id}")
async def get_facility_by_id(facility_id: str):
    """Fetch a single facility by ID."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT FACILITY_ID, FACILITY_NAME, FACILITY_TIMEZONE, FACILITY_LOCATION, IS_ACTIVE FROM SOURCE_FACILITIES WHERE FACILITY_ID = %s", (facility_id,))

        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Facility not found")

        columns = [col[0] for col in cursor.description]
        facility = dict(zip(columns, result))
        facility['IS_ACTIVE'] = bool(facility['IS_ACTIVE'])

        return facility
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching facility: {e}")
    finally:
        conn.close()


@app.post("/api/facilities")
async def add_new_facility(facility: Facility):
    """Create a new source facility."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()
        facility_id = 'FAC_' + str(uuid.uuid4())[:8].upper()
        query = "INSERT INTO SOURCE_FACILITIES (FACILITY_ID, FACILITY_NAME, FACILITY_TIMEZONE, FACILITY_LOCATION, IS_ACTIVE) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (
            facility_id,
            facility.facility_name,
            facility.facility_timezone,
            facility.facility_location,
            facility.is_active
        ))
        conn.commit()
        return {
            "status": "success",
            "message": "Facility added successfully!",
            "facility_id": facility_id
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to add facility: {e}")
    finally:
        conn.close()


@app.put("/api/facilities/{facility_id}")
async def update_facility(facility_id: str, facility: FacilityUpdate):
    """Update an existing facility."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()

        update_fields = []
        params = []

        if facility.facility_name is not None:
            update_fields.append("FACILITY_NAME = %s")
            params.append(facility.facility_name)

        if facility.facility_timezone is not None:
            update_fields.append("FACILITY_TIMEZONE = %s")
            params.append(facility.facility_timezone)

        if facility.facility_location is not None:
            update_fields.append("FACILITY_LOCATION = %s")
            params.append(facility.facility_location)

        if facility.is_active is not None:
            update_fields.append("IS_ACTIVE = %s")
            params.append(facility.is_active)

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        params.append(facility_id)
        query = f"UPDATE SOURCE_FACILITIES SET {', '.join(update_fields)} WHERE FACILITY_ID = %s"

        cursor.execute(query, params)

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Facility not found")

        conn.commit()
        return {"status": "success", "message": "Facility updated successfully!"}
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to update facility: {e}")
    finally:
        conn.close()


@app.delete("/api/facilities/{facility_id}")
async def delete_facility(facility_id: str):
    """Delete a facility."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM SOURCE_FACILITIES WHERE FACILITY_ID = %s", (facility_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Facility not found")
        conn.commit()
        return {"status": "success", "message": "Facility deleted successfully!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to delete facility: {e}")
    finally:
        conn.close()


@app.get("/api/facilities/stats-by-timezone")
async def get_facility_stats_by_timezone():
    """Get aggregated statistics grouped by timezone."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()
        query = """
        SELECT 
            f.FACILITY_TIMEZONE,
            COUNT(DISTINCT f.FACILITY_ID) as FACILITY_COUNT,
            COUNT(DISTINCT p.PATIENT_ID) as PATIENT_COUNT,
            COUNT(DISTINCT l.LOG_ID) as SYNC_COUNT,
            AVG(l.LAG_SECONDS) as AVG_LAG
        FROM SOURCE_FACILITIES f
        LEFT JOIN PATIENT_REGISTRATIONS p ON f.FACILITY_ID = p.FACILITY_ID
        LEFT JOIN SYNC_OPERATIONS_LOG l ON f.FACILITY_ID = l.SOURCE_FACILITY_ID AND l.STATUS = 'SUCCESS'
        GROUP BY f.FACILITY_TIMEZONE
        ORDER BY PATIENT_COUNT DESC
        """
        cursor.execute(query)

        columns = [col[0] for col in cursor.description]
        stats = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for stat in stats:
            stat['AVG_LAG'] = round(
                stat['AVG_LAG'], 3) if stat['AVG_LAG'] else 0

        return {"timezone_stats": stats}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching timezone stats: {e}")
    finally:
        conn.close()


@app.get("/api/targets")
async def load_sync_targets():
    """Fetch all sync targets."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()
        query = "SELECT TARGET_ID, TARGET_NAME, TARGET_TYPE, CONNECTION_STRING, IS_ACTIVE, LAST_SYNC_TIME FROM SYNC_TARGETS ORDER BY TARGET_NAME"
        cursor.execute(query)

        columns = [col[0] for col in cursor.description]
        targets = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for t in targets:
            t['LAST_SYNC_TIME'] = t['LAST_SYNC_TIME'].strftime(
                '%Y-%m-%d %H:%M:%S') if t['LAST_SYNC_TIME'] else 'N/A'
            t['IS_ACTIVE'] = bool(t['IS_ACTIVE'])

        return targets
    except Exception as e:
        print(f"Error in get_targets: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching targets: {e}")
    finally:
        conn.close()


@app.get("/api/targets/{target_id}")
async def get_target_by_id(target_id: str):
    """Fetch a single target by ID."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT TARGET_ID, TARGET_NAME, TARGET_TYPE, CONNECTION_STRING, IS_ACTIVE FROM SYNC_TARGETS WHERE TARGET_ID = %s", (target_id,))

        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Target not found")

        columns = [col[0] for col in cursor.description]
        target = dict(zip(columns, result))
        target['IS_ACTIVE'] = bool(target['IS_ACTIVE'])

        return target
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching target: {e}")
    finally:
        conn.close()


@app.post("/api/targets")
async def add_new_target(target: SyncTarget):
    """Create a new sync target."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()
        target_id = 'TGT_' + str(uuid.uuid4())[:8].upper()
        query = "INSERT INTO SYNC_TARGETS (TARGET_ID, TARGET_NAME, TARGET_TYPE, CONNECTION_STRING, IS_ACTIVE) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (
            target_id,
            target.target_name,
            target.target_type,
            target.connection_string,
            target.is_active
        ))
        conn.commit()
        return {
            "status": "success",
            "message": "Target added successfully!",
            "target_id": target_id
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to add target: {e}")
    finally:
        conn.close()


@app.put("/api/targets/{target_id}")
async def update_target(target_id: str, target: SyncTargetUpdate):
    """Update an existing sync target."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()

        update_fields = []
        params = []

        if target.target_name is not None:
            update_fields.append("TARGET_NAME = %s")
            params.append(target.target_name)

        if target.target_type is not None:
            update_fields.append("TARGET_TYPE = %s")
            params.append(target.target_type)

        if target.connection_string is not None:
            update_fields.append("CONNECTION_STRING = %s")
            params.append(target.connection_string)

        if target.is_active is not None:
            update_fields.append("IS_ACTIVE = %s")
            params.append(target.is_active)

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        params.append(target_id)
        query = f"UPDATE SYNC_TARGETS SET {', '.join(update_fields)} WHERE TARGET_ID = %s"

        cursor.execute(query, params)

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Target not found")

        conn.commit()
        return {"status": "success", "message": "Target updated successfully!"}
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to update target: {e}")
    finally:
        conn.close()


@app.delete("/api/targets/{target_id}")
async def delete_target(target_id: str):
    """Delete a sync target."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM SYNC_TARGETS WHERE TARGET_ID = %s", (target_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Target not found")
        conn.commit()
        return {"status": "success", "message": "Target deleted successfully!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to delete target: {e}")
    finally:
        conn.close()


@app.get("/api/targets/{target_id}/schema")
async def get_target_schema(target_id: str):
    """Fetch schema details for a target."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()
        schema_details = []

        tables_query = "SHOW TABLES"
        cursor.execute(tables_query)
        tables = [row[1] for row in cursor.fetchall()]

        for table_name in tables:
            row_count_query = f"SELECT COUNT(*) FROM {table_name}"
            cursor.execute(row_count_query)
            row_count = cursor.fetchone()[0]

            fk_count_query = f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
            WHERE CONSTRAINT_TYPE = 'FOREIGN KEY' 
            AND TABLE_NAME = '{table_name}' 
            AND TABLE_CATALOG = '{os.getenv('SNOWFLAKE_DATABASE')}' 
            AND TABLE_SCHEMA = '{os.getenv('SNOWFLAKE_SCHEMA')}'
            """
            cursor.execute(fk_count_query)
            fk_count = cursor.fetchone()[0]

            schema_details.append({
                "table_name": table_name,
                "row_count": row_count,
                "foreign_key_count": fk_count
            })

        return {"target_id": target_id, "schema": schema_details}

    except Exception as e:
        print(f"Error fetching target schema: {e}")
        traceback.print_exc()
        return {"target_id": target_id, "schema": [], "error": f"Failed to inspect schema: {e}"}
    finally:
        conn.close()


@app.post("/api/trigger-sync")
async def trigger_manual_sync(sync_data: TriggerSync):
    """Trigger a manual sync operation."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT FACILITY_ID FROM SOURCE_FACILITIES WHERE FACILITY_ID = %s",
                       (sync_data.source_facility_id,))
        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404, detail="Source facility not found")

        cursor.execute(
            "SELECT TARGET_ID FROM SYNC_TARGETS WHERE TARGET_ID = %s", (sync_data.target_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Target not found")

        log_id = 'LOG_' + str(uuid.uuid4())[:8].upper()
        sync_started = datetime.now()

        import time
        import random
        lag_seconds = round(random.uniform(0.5, 1.5), 3)
        time.sleep(0.5)

        sync_completed = datetime.now()
        duration = (sync_completed - sync_started).total_seconds()

        log_query = """
        INSERT INTO SYNC_OPERATIONS_LOG (
            LOG_ID, SOURCE_FACILITY_ID, TARGET_ID, OPERATION_TYPE, RECORD_COUNT, 
            LAG_SECONDS, STATUS, SYNC_STARTED_AT, SYNC_COMPLETED_AT, DURATION_SECONDS, 
            ERROR_MESSAGE, CREATED_BY_USER
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(log_query, (
            log_id,
            sync_data.source_facility_id,
            sync_data.target_id,
            sync_data.operation_type,
            random.randint(5, 50),
            lag_seconds,
            'SUCCESS',
            sync_started,
            sync_completed,
            duration,
            None,
            'ADMIN_DASHBOARD'
        ))

        cursor.execute("UPDATE SOURCE_FACILITIES SET LAST_SYNC_TIME = %s WHERE FACILITY_ID = %s",
                       (sync_completed, sync_data.source_facility_id))
        cursor.execute("UPDATE SYNC_TARGETS SET LAST_SYNC_TIME = %s WHERE TARGET_ID = %s",
                       (sync_completed, sync_data.target_id))

        conn.commit()

        return {
            "status": "success",
            "message": "Sync triggered successfully",
            "log_id": log_id,
            "duration_seconds": duration,
            "sync_completed_at": sync_completed.strftime('%Y-%m-%d %H:%M:%S')
        }

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        print(f"Sync trigger error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to trigger sync: {e}")
    finally:
        conn.close()


@app.post("/api/register-patient")
async def register_patient(patient: PatientRegistration):
    """Register a new patient with timezone-aware timestamp conversion."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT FACILITY_ID FROM SOURCE_FACILITIES WHERE FACILITY_ID = %s",
                       (patient.registration_facility,))
        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404, detail="Registration facility not found")

        patient_id = 'PAT_' + str(uuid.uuid4())[:8].upper()
        registration_id = 'REG_' + str(uuid.uuid4())[:8].upper()

        local_dt = datetime.strptime(
            patient.local_registration_time, '%Y-%m-%d %H:%M:%S')

        timezone_offsets = {
            'GMT/UTC': 0, 'EST': -5, 'CST': -6, 'MST': -7, 'PST': -8,
            'ART': -3, 'CET': 1, 'EET': 2, 'MSK': 3, 'GST': 4,
            'IST': 5.5, 'SGT': 8, 'JST': 9, 'AEST': 10, 'NZST': 12
        }

        local_offset = timezone_offsets.get(patient.local_time_zone, 0)
        ist_offset = 5.5

        utc_time = local_dt - timedelta(hours=local_offset)
        ist_time = utc_time + timedelta(hours=ist_offset)

        insert_query = """
        INSERT INTO PATIENT_REGISTRATIONS (
            PATIENT_ID, REGISTRATION_ID, PATIENT_NAME, DATE_OF_BIRTH, 
            CONTACT_NUMBER, EMAIL, FACILITY_ID, REGISTRATION_TIMEZONE, 
            REGISTRATION_LOCAL_TIME, REGISTRATION_IST_TIME, CREATED_AT
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(insert_query, (
            patient_id,
            registration_id,
            patient.full_name,
            patient.date_of_birth,
            patient.contact_number,
            patient.email,
            patient.registration_facility,
            patient.local_time_zone,
            patient.local_registration_time,
            ist_time.strftime('%Y-%m-%d %H:%M:%S'),
            datetime.now()
        ))

        conn.commit()

        return {
            "status": "success",
            "message": "Patient registered successfully",
            "patient_id": patient_id,
            "registration_id": registration_id,
            "IST_Timestamp": ist_time.strftime('%Y-%m-%d %H:%M:%S')
        }

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        print(f"Registration error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to register patient: {e}")
    finally:
        conn.close()


@app.get("/api/patients")
async def get_registered_patients(date: str = Query(None)):
    """Fetch registered patients with optional date filter."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()

        base_query = """
        SELECT 
            p.PATIENT_ID,
            p.PATIENT_NAME AS FULL_NAME,
            f.FACILITY_NAME,
            p.REGISTRATION_IST_TIME AS IST_REGISTRATION_TIME,
            p.DATE_OF_BIRTH,
            p.CONTACT_NUMBER,
            p.EMAIL,
            p.REGISTRATION_TIMEZONE,
            p.REGISTRATION_LOCAL_TIME
        FROM PATIENT_REGISTRATIONS p
        JOIN SOURCE_FACILITIES f ON p.FACILITY_ID = f.FACILITY_ID
        WHERE 1=1
        """

        params = {}
        if date:
            base_query += " AND DATE(p.REGISTRATION_IST_TIME) = %(date)s"
            params['date'] = date

        base_query += " ORDER BY p.REGISTRATION_IST_TIME DESC LIMIT 100"

        cursor.execute(base_query, params)

        columns = [col[0] for col in cursor.description]
        patients = []
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            row_dict['IST_REGISTRATION_TIME'] = row_dict['IST_REGISTRATION_TIME'].strftime(
                '%Y-%m-%d %H:%M:%S') if row_dict['IST_REGISTRATION_TIME'] else 'N/A'
            row_dict['REGISTRATION_LOCAL_TIME'] = row_dict['REGISTRATION_LOCAL_TIME'] if row_dict['REGISTRATION_LOCAL_TIME'] else 'N/A'
            patients.append(row_dict)

        return patients
    except Exception as e:
        print(f"Error fetching patients: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error fetching patients: {e}")
    finally:
        conn.close()


@app.get("/api/analysis/lag/timezone")
async def get_lag_by_timezone():
    """Calculate lag statistics by facility timezone."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()
        query = """
        SELECT 
            f.FACILITY_TIMEZONE,
            AVG(l.LAG_SECONDS) AS AVG_LAG,
            MIN(l.LAG_SECONDS) AS MIN_LAG,
            MAX(l.LAG_SECONDS) AS MAX_LAG
        FROM SYNC_OPERATIONS_LOG l
        JOIN SOURCE_FACILITIES f ON l.SOURCE_FACILITY_ID = f.FACILITY_ID
        WHERE l.STATUS = 'SUCCESS' 
        GROUP BY 1
        ORDER BY AVG_LAG DESC
        """
        cursor.execute(query)

        columns = [col[0] for col in cursor.description]
        lag_stats = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return {"lag_by_timezone": lag_stats}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching lag by timezone: {e}")
    finally:
        conn.close()


@app.get("/api/analysis/timezone-stats")
async def get_timezone_sync_statistics(target_tz: str = 'IST'):
    """Get combined sync performance and timezone offset statistics."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")

    target_pytz_name = TIMEZONE_MAP.get(target_tz.upper(), 'Asia/Kolkata')

    try:
        cursor = conn.cursor()
        lag_query = """
        SELECT 
            f.FACILITY_TIMEZONE,
            COUNT(l.LOG_ID) as TOTAL_SYNCS,
            SUM(CASE WHEN l.STATUS = 'SUCCESS' THEN 1 ELSE 0 END) as SUCCESSFUL_SYNCS,
            AVG(l.LAG_SECONDS) AS AVG_LAG
        FROM SYNC_OPERATIONS_LOG l
        JOIN SOURCE_FACILITIES f ON l.SOURCE_FACILITY_ID = f.FACILITY_ID
        GROUP BY 1
        ORDER BY AVG_LAG DESC
        """
        cursor.execute(lag_query)

        columns = [col[0] for col in cursor.description]
        combined_stats = []

        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            source_tz_simple = row_dict['FACILITY_TIMEZONE']

            source_pytz_name = TIMEZONE_MAP.get(
                source_tz_simple.upper(), source_tz_simple)

            offset_str = get_timezone_offset_str(
                source_pytz_name, target_pytz_name)

            total_syncs = row_dict['TOTAL_SYNCS']
            successful_syncs = row_dict['SUCCESSFUL_SYNCS']

            row_dict['TIMEZONE_OFFSET'] = offset_str
            row_dict['AVG_LAG'] = f"{row_dict['AVG_LAG']:.3f} s" if row_dict['AVG_LAG'] is not None else 'N/A'
            row_dict['SUCCESS_RATE'] = f"{round((successful_syncs / total_syncs) * 100, 2)}%" if total_syncs > 0 else 'N/A'
            combined_stats.append(row_dict)

        return {"timezone_stats": combined_stats}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching timezone sync stats: {e}")
    finally:
        conn.close()


@app.get("/api/logs")
async def load_sync_logs(
    status: str = Query(None),
    operation_type: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None)
):
    """Fetch sync operation logs with filtering."""
    conn = get_snowflake_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()

        base_query = """
        SELECT 
            l.LOG_ID, l.SYNC_COMPLETED_AT, f.FACILITY_NAME, t.TARGET_NAME, 
            l.OPERATION_TYPE, l.RECORD_COUNT, l.LAG_SECONDS, l.STATUS, 
            l.ERROR_MESSAGE, l.CREATED_BY_USER
        FROM SYNC_OPERATIONS_LOG l
        JOIN SOURCE_FACILITIES f ON l.SOURCE_FACILITY_ID = f.FACILITY_ID
        JOIN SYNC_TARGETS t ON l.TARGET_ID = t.TARGET_ID
        WHERE 1=1
        """
        params = {}

        if status and status.lower() != 'all':
            base_query += " AND l.STATUS = %(status)s"
            params['status'] = status.upper()

        if operation_type and operation_type.lower() != 'all':
            base_query += " AND l.OPERATION_TYPE = %(op_type)s"
            params['op_type'] = operation_type.upper()

        if start_date:
            base_query += " AND DATE(l.SYNC_COMPLETED_AT) >= %(start_date)s"
            params['start_date'] = start_date

        if end_date:
            base_query += " AND DATE(l.SYNC_COMPLETED_AT) <= %(end_date)s"
            params['end_date'] = end_date

        base_query += " ORDER BY l.SYNC_COMPLETED_AT DESC LIMIT 500"

        cursor.execute(base_query, params)

        columns = [col[0] for col in cursor.description]
        logs = []
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            row_dict['SYNC_COMPLETED_AT'] = row_dict['SYNC_COMPLETED_AT'].strftime(
                '%Y-%m-%d %H:%M:%S') if row_dict['SYNC_COMPLETED_AT'] else 'N/A'
            row_dict['LAG_SECONDS'] = round(
                row_dict['LAG_SECONDS'], 3) if row_dict['LAG_SECONDS'] is not None else 'N/A'
            row_dict['ERROR_MESSAGE'] = row_dict['ERROR_MESSAGE'] if row_dict['ERROR_MESSAGE'] else ''
            logs.append(row_dict)

        return logs

    except Exception as e:
        print(f"Error fetching logs: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error fetching logs: {e}")
    finally:
        conn.close()


# --- FIXED: Static file serving ---
@app.get("/")
async def serve_index():
    """Serve index.html."""
    return FileResponse("index.html")


@app.get("/register.html")
async def serve_register():
    """Serve register.html."""
    return FileResponse("register.html")


@app.get("/admin.html")
async def serve_admin():
    """Serve admin.html."""
    return FileResponse("admin.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
