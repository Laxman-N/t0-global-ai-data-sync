# Global AI Data Sync Dashboard

A time zone-aware patient treatment data management system with FastAPI backend and Snowflake integration.

## Features

- 🌍 Global time zone support (IST, EST, PST, GMT, and more)
- 📊 Real-time data synchronization with Snowflake
- 🏥 Patient treatment record management
- 🕐 Automatic time zone conversion to IST reporting standard
- 🎨 Modern, responsive UI with Tailwind CSS

## Tech Stack

**Backend:**
- FastAPI
- Snowflake Connector for Python
- Python-dotenv

**Frontend:**
- HTML5
- Tailwind CSS
- Lucide Icons
- Vanilla JavaScript

## Prerequisites

- Python 3.8+
- Snowflake account with appropriate credentials
- pip package manager

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

2. Create a virtual environment:
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory with your Snowflake credentials:
```env
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
```

## Database Setup

Create the required table in Snowflake:

```sql
CREATE TABLE PATIENT_TREATMENT_RECORDS (
    HOSPITAL_ID VARCHAR(100),
    PATIENT_ID VARCHAR(100),
    LOCAL_TIMESTAMP TIMESTAMP,
    TREATMENT_TYPE VARCHAR(200),
    TREATMENT_NOTES VARIANT,
    UPLOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

## Running the Application

1. Start the FastAPI backend:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

2. Open the frontend:
   - Navigate to `admin-dashboard/index.html`
   - Open it in a web browser or serve it with a local server

## API Endpoints

### GET `/report/summary`
Fetches connection status and database information.

**Response:**
```json
{
    "status": "Success",
    "message": "Connection and query executed successfully.",
    "current_db_time": "2025-10-07 12:30:45",
    "connected_schema": "YOUR_DATABASE.YOUR_SCHEMA"
}
```

### POST `/data/upload`
Uploads patient treatment data to Snowflake.

**Request Body:**
```json
{
    "hospital_id": "HOSPITAL_A",
    "patient_id": "P_001",
    "local_timestamp": "2025-10-07 15:30:00",
    "treatment_type": "Medication_Administration",
    "treatment_notes": {
        "drug": "Aspirin",
        "dose": "5mg"
    }
}
```

## Time Zone Support

The application supports multiple time zones including:
- IST (Indian Standard Time) - Default reporting standard
- EST, CST, MST, PST (US Time Zones)
- GMT/UTC, CET, EET (European Time Zones)
- GST, SGT, JST, AEST, NZST (Asia-Pacific Time Zones)

All timestamps are automatically converted to IST for standardized reporting.

## Project Structure

```
TO-AI-AGENT-SYSTEM/
├── admin-dashboard/
│   └── index.html          # Frontend dashboard
├── backend/
│   ├── main.py             # FastAPI application
│   ├── config.py           # Configuration (if any)
│   ├── requirements.txt    # Python dependencies
│   ├── .env                # Environment variables (not committed)
│   └── rsa_key.p8          # Snowflake key (not committed)
├── .gitignore
└── README.md
```

## Security Notes

⚠️ **IMPORTANT:** Never commit the following files:
- `.env` (contains passwords and credentials)
- `rsa_key.p8` / `rsa_key.pub` (Snowflake authentication keys)
- Any files containing sensitive information

These files are automatically excluded by the `.gitignore`.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues or questions, please open an issue in the GitHub repository.

## Acknowledgments

- Snowflake for database infrastructure
- FastAPI for the backend framework
- Tailwind CSS for styling