Global AI Data Sync Dashboard
A time zone-aware patient treatment data management system with FastAPI backend and Snowflake integration.

Features
🌍 Global time zone support (IST, EST, PST, GMT, and more)

📊 Real-time data synchronization with Snowflake

🏥 Patient treatment record management

🕐 Automatic time zone conversion to IST reporting standard

🎨 Modern, responsive UI with Tailwind CSS

Tech Stack
Backend:

FastAPI

Snowflake Connector for Python

Python-dotenv

Frontend:

HTML5

Tailwind CSS

Lucide Icons

Vanilla JavaScript

Prerequisites
Python 3.8+

Snowflake account with appropriate credentials

pip package manager

Installation
Clone the repository:

git clone [https://github.com/Laxman-N/t0-global-ai-data-sync.git](https://github.com/Laxman-N/t0-global-ai-data-sync.git)
cd t0-ai-agent-system

Create a virtual environment:

python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

Install dependencies (requires backend/requirements.txt):

pip install -r backend/requirements.txt

Create a .env file in the backend directory with your Snowflake credentials (see Security Notes):

SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema

Database Setup
Refer to SNOWFLAKE_SETUP.md for full configuration, but run this command to create the primary table:

CREATE TABLE PATIENT_TREATMENTS (
    TREATMENT_ID VARCHAR(50) PRIMARY KEY,
    HOSPITAL_ID VARCHAR(50) NOT NULL,
    PATIENT_ID VARCHAR(50) NOT NULL,
    TREATMENT_TYPE VARCHAR(100),
    TREATMENT_NOTES VARIANT,
    LOCAL_TIMESTAMP TIMESTAMP_TZ,
    T0_UTC_TIMESTAMP TIMESTAMP_NTZ NOT NULL,
    INGESTION_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

Running the Application
Start the FastAPI backend:

cd backend
# Note: Use port 8001 if port 8000 is unavailable
uvicorn main:app --reload --port 8001

Open the frontend: Navigate to admin-dashboard/index.html and open it in a web browser.

API Endpoints
(API Endpoints section content remains the same)

Time Zone Support
(Time Zone Support section content remains the same)

Project Structure
t0-ai-agent-system/
├── admin-dashboard/
│   └── index.html          # Frontend dashboard
├── backend/
│   ├── ai_agent/           # Core Time Sync Logic
│   │   └── time_sync_agent.py
│   ├── main.py             # FastAPI application
│   ├── config.py           # Configuration details
│   └── requirements.txt    # Python dependencies
├── .gitignore
└── README.md

Security Notes
⚠️ IMPORTANT: Never commit the following files:

.env (contains passwords and credentials)

rsa_key.p8 / rsa_key.pub (Snowflake authentication keys)

Contributing
(Contributing section content remains the same)

License
This project is licensed under the MIT License - see the LICENSE.md file for details.