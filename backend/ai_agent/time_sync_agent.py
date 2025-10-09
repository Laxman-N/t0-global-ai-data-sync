import pytz
from datetime import datetime, timezone


class T0AIAgent:
    """
    The T0 AI Agent handles time zone detection, synchronization, and logging.
    It maps a facility ID to a specific timezone and converts local timestamps 
    to a unified T0 (UTC) timestamp, logging the event details.
    """

    def __init__(self):
        # Enhanced timezone map with offset information for better handling
        self.TIMEZONE_MAP = {
            'FAC_001': {'zone': 'Asia/Kolkata', 'offset': 5.5, 'name': 'IST'},
            'FAC_002': {'zone': 'America/New_York', 'offset': -5.0, 'name': 'EST'},
            'FAC_003': {'zone': 'Europe/London', 'offset': 0.0, 'name': 'GMT'},
            'FAC_004': {'zone': 'Asia/Tokyo', 'offset': 9.0, 'name': 'JST'},
            'FAC_005': {'zone': 'Australia/Sydney', 'offset': 10.0, 'name': 'AEST'},
            'FAC_006': {'zone': 'Europe/Paris', 'offset': 1.0, 'name': 'CET'},
            'FAC_007': {'zone': 'Asia/Dubai', 'offset': 4.0, 'name': 'GST'},
            'FAC_008': {'zone': 'America/Los_Angeles', 'offset': -8.0, 'name': 'PST'}
        }

    def detect_timezone(self, hospital_id: str) -> str:
        """
        Detects the time zone based on a predefined hospital mapping.
        """
        tz_name = self.TIMEZONE_MAP.get(hospital_id)
        if not tz_name:
            raise ValueError(
                f"Unknown Hospital ID: {hospital_id}. Cannot determine timezone.")
        return tz_name

    def synchronize_timestamp(self, hospital_id: str, local_datetime_str: str) -> dict:
        """
        Converts a local time string from a specific hospital to a unified T0 (UTC) time.

        Args:
            hospital_id: Identifier for the hospital (e.g., "IND001").
            local_datetime_str: The timestamp string from the hospital (e.g., "2025-10-25 14:30:00").

        Returns:
            A dictionary containing the local time, T0 (UTC) time, and log details.
        """
        log_entry = {
            "hospital_id": hospital_id,
            "local_timestamp_str": local_datetime_str,
            "local_timezone": "N/A",
            "t0_utc_timestamp": None,
            "conversion_status": "FAILED",
        }

        try:
            # 1. Detect Time Zone
            tz_name = self.detect_timezone(hospital_id)
            log_entry["local_timezone"] = tz_name

            # 2. Parse Local Datetime String
            naive_dt = datetime.strptime(
                local_datetime_str, '%Y-%m-%d %H:%M:%S')

            # 3. Localize the naive datetime object (handles DST automatically via pytz)
            local_tz = pytz.timezone(tz_name)
            local_dt_aware = local_tz.localize(naive_dt, is_dst=None)

            # 4. Convert to UTC (T0)
            utc_dt = local_dt_aware.astimezone(pytz.utc)

            # Store as a timezone-naive datetime object for Snowflake's TIMESTAMP_NTZ column
            t0_utc_naive = utc_dt.replace(tzinfo=None)

            log_entry["t0_utc_timestamp"] = t0_utc_naive
            log_entry["local_timestamp_aware"] = local_dt_aware
            log_entry["conversion_status"] = "SUCCESS"

            return {
                "t0_utc_time": t0_utc_naive.strftime('%Y-%m-%d %H:%M:%S'),
                "local_time_aware": local_dt_aware.isoformat(),
                "log_details": log_entry
            }

        except ValueError as e:
            log_entry["conversion_status"] = f"ERROR: {str(e)}"
            return {"t0_utc_time": None, "log_details": log_entry}
        except Exception as e:
            log_entry["conversion_status"] = f"CRITICAL ERROR: {str(e)}"
            return {"t0_utc_time": None, "log_details": log_entry}
