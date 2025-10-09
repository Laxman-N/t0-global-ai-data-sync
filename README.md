# 🌍 Global AI Data Sync System

A comprehensive multi-timezone healthcare data synchronization platform with real-time patient registration, facility management, and automated sync operations powered by FastAPI and Snowflake.

## 📖 Overview

This system enables healthcare organizations to manage patient data across multiple global facilities while automatically handling timezone conversions, synchronization operations, and performance analytics. All timestamps are normalized to IST (Indian Standard Time) for standardized reporting and analysis.

## ✨ Key Features

**🏥 Patient Management**
- Multi-timezone patient registration supporting 15+ global time zones
- Automatic timestamp conversion to IST for standardized reporting
- Real-time calendar view for tracking daily registrations
- Comprehensive patient records with demographics and facility associations

**🏢 Facility Management**
- Global facility network spanning multiple continents
- Timezone-aware operations with each facility in its local timezone
- Active status tracking and monitoring
- Aggregated statistics by timezone and location

**🔄 Sync Operations**
- Manual and automated data synchronization triggers
- Comprehensive operation logging with lag metrics
- Multi-target support (Snowflake, S3, and more)
- Real-time performance analytics and monitoring

**📊 Advanced Analytics**
- Timezone offset analysis comparing performance across regions
- Lag statistics identifying sync bottlenecks
- Success rate tracking for data quality monitoring
- Interactive visualizations with Chart.js

## 🛠 Technology Stack

**Backend**
- FastAPI - Modern async web framework with automatic API documentation
- Snowflake Connector - Enterprise cloud data warehouse integration
- Python-dotenv - Secure environment variable management
- PyTZ - Timezone calculations and conversions

**Frontend**
- Vanilla JavaScript - No framework dependencies
- Chart.js - Interactive data visualizations
- Responsive CSS - Mobile-first design
- Modern HTML5 - Semantic and accessible markup

**Database**
- Snowflake - Scalable cloud data warehouse with native timezone support

## 📋 Prerequisites

- Python 3.8 or higher
- Active Snowflake account with admin privileges
- Modern web browser (Chrome, Firefox, Safari, or Edge)
- Git for version control

## 🚀 Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Laxman-N/t0-global-ai-data-sync.git
cd t0-global-ai-data-sync
```

### 2️⃣ Set Up Python Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HEALTHCARE_DB
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

**Security Note:** Never commit the `.env` file to version control.

## 💾 Database Setup

### Create Database and Schema

```sql
CREATE DATABASE IF NOT EXISTS HEALTHCARE_DB;
USE DATABASE HEALTHCARE_DB;
CREATE SCHEMA IF NOT EXISTS PUBLIC;
```

### Create Required Tables

**Source Facilities:**
```sql
CREATE TABLE SOURCE_FACILITIES (
    FACILITY_ID VARCHAR(50) PRIMARY KEY,
    FACILITY_NAME VARCHAR(200) NOT NULL,
    FACILITY_TIMEZONE VARCHAR(50) NOT NULL,
    FACILITY_LOCATION VARCHAR(100),
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    LAST_SYNC_TIME TIMESTAMP_NTZ,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

**Sync Targets:**
```sql
CREATE TABLE SYNC_TARGETS (
    TARGET_ID VARCHAR(50) PRIMARY KEY,
    TARGET_NAME VARCHAR(200) NOT NULL,
    TARGET_TYPE VARCHAR(50) NOT NULL,
    CONNECTION_STRING TEXT NOT NULL,
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    LAST_SYNC_TIME TIMESTAMP_NTZ,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

**Patient Registrations:**
```sql
CREATE TABLE PATIENT_REGISTRATIONS (
    PATIENT_ID VARCHAR(50) PRIMARY KEY,
    REGISTRATION_ID VARCHAR(50) UNIQUE NOT NULL,
    PATIENT_NAME VARCHAR(200) NOT NULL,
    DATE_OF_BIRTH DATE NOT NULL,
    CONTACT_NUMBER VARCHAR(50) NOT NULL,
    EMAIL VARCHAR(200),
    FACILITY_ID VARCHAR(50) NOT NULL,
    REGISTRATION_TIMEZONE VARCHAR(50) NOT NULL,
    REGISTRATION_LOCAL_TIME VARCHAR(50) NOT NULL,
    REGISTRATION_IST_TIME TIMESTAMP_NTZ NOT NULL,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (FACILITY_ID) REFERENCES SOURCE_FACILITIES(FACILITY_ID)
);
```

**Sync Operations Log:**
```sql
CREATE TABLE SYNC_OPERATIONS_LOG (
    LOG_ID VARCHAR(50) PRIMARY KEY,
    SOURCE_FACILITY_ID VARCHAR(50) NOT NULL,
    TARGET_ID VARCHAR(50) NOT NULL,
    OPERATION_TYPE VARCHAR(50) NOT NULL,
    RECORD_COUNT INTEGER,
    LAG_SECONDS FLOAT,
    STATUS VARCHAR(20) NOT NULL,
    SYNC_STARTED_AT TIMESTAMP_NTZ,
    SYNC_COMPLETED_AT TIMESTAMP_NTZ,
    DURATION_SECONDS FLOAT,
    ERROR_MESSAGE TEXT,
    CREATED_BY_USER VARCHAR(100),
    FOREIGN KEY (SOURCE_FACILITY_ID) REFERENCES SOURCE_FACILITIES(FACILITY_ID),
    FOREIGN KEY (TARGET_ID) REFERENCES SYNC_TARGETS(TARGET_ID)
);
```

## 🎯 Running the Application

### Start the Backend Server

```bash
cd backend
python main.py
```

The API will be available at:
- Application: `http://localhost:8000`
- Interactive API Docs: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

### Access the Frontend

Open your browser and navigate to:
- Home: `http://localhost:8000/`
- Patient Registration: `http://localhost:8000/register.html`
- Admin Dashboard: `http://localhost:8000/admin.html`

## 📡 API Reference

### Core Endpoints

**Health Check**
```http
GET /health
```

**Dashboard Overview**
```http
GET /api/dashboard/overview
```

**List Facilities**
```http
GET /api/facilities?timezone=IST
```

**Register Patient**
```http
POST /api/register-patient
Content-Type: application/json

{
    "full_name": "John Doe",
    "date_of_birth": "1990-01-15",
    "contact_number": "+1-234-567-8900",
    "email": "john.doe@example.com",
    "registration_facility": "FAC_12345678",
    "local_time_zone": "EST",
    "local_registration_time": "2025-10-10 09:30:00"
}
```

**Trigger Manual Sync**
```http
POST /api/trigger-sync
Content-Type: application/json

{
    "source_facility_id": "FAC_12345678",
    "target_id": "TGT_87654321",
    "operation_type": "MANUAL_SYNC"
}
```

For complete API documentation, visit `http://localhost:8000/docs` when the server is running.

## 🌐 Supported Time Zones

The system supports automatic conversion between these timezones and IST:

- **North America:** EST, CST, MST, PST
- **South America:** ART
- **Europe:** GMT/UTC, CET, EET, MSK
- **Middle East:** GST
- **Asia:** IST (standard), SGT, JST
- **Oceania:** AEST, NZST

All timestamps are automatically converted to IST (UTC+5:30) for standardized reporting.

## 📁 Project Structure

```
t0-global-ai-data-sync/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment variables (not in git)
│
├── admin-dashboard/
│   ├── index.html              # Home page
│   ├── register.html           # Patient registration
│   └── admin.html              # Admin dashboard
│
├── .gitignore
├── README.md
└── LICENSE.md
```

## 🔧 Troubleshooting

**Database Connection Failed**
- Verify `.env` file exists in the `backend/` directory
- Check that Snowflake credentials are correct
- Ensure the warehouse is running in Snowflake console

**CORS Policy Blocking Requests**
- Confirm `main.py` has `allowed_origins = ["*"]` for development
- Restart the FastAPI server after changes

**Error Loading Facilities**
- Verify all tables exist in Snowflake
- Check browser console (F12) for detailed errors
- Ensure `register.html` uses the correct API_BASE_URL

**Module Not Found Errors**
```bash
pip install -r backend/requirements.txt --upgrade
```

## 🔐 Security Best Practices

**Never commit these files:**
- `.env` - Database credentials
- `*.log` - Application logs
- `venv/` - Virtual environment

**Production Recommendations:**
- Use secret management services (AWS Secrets Manager, Azure Key Vault)
- Enable HTTPS with TLS certificates
- Implement role-based access control in Snowflake
- Enable multi-factor authentication
- Regular security audits and access log monitoring
- Restrict CORS to specific origins
- Implement API rate limiting

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and test thoroughly
4. Commit with semantic messages (`git commit -m "feat: Add amazing feature"`)
5. Push to your fork (`git push origin feature/amazing-feature`)
6. Open a Pull Request with a detailed description

**Commit Convention:**
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation updates
- `refactor:` Code restructuring
- `test:` Test additions
- `chore:` Maintenance tasks

## 📄 License

This project is licensed under the MIT License. See LICENSE.md for details.

## 💬 Support

- 🐛 Report bugs via GitHub Issues
- 💡 Request features via GitHub Discussions
- 📧 Email: laxman.support@example.com

## 🙏 Acknowledgments

Built with these amazing open-source technologies:
- FastAPI - Modern Python web framework
- Snowflake - Cloud data warehouse platform
- Chart.js - JavaScript charting library
- PyTZ - Timezone calculations for Python
- Uvicorn - Lightning-fast ASGI server

---

**Built with ❤️ for global healthcare data synchronization**
