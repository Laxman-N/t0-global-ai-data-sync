# 🌍 Global AI Data Sync Dashboard

> A sophisticated, time zone-aware patient treatment data management system built with FastAPI and Snowflake integration.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE.md)

---

## ✨ Key Features

- **🌐 Global Time Zone Support** - Seamlessly handles IST, EST, PST, GMT, and 15+ time zones
- **⚡ Real-time Synchronization** - Instant data sync with Snowflake cloud infrastructure
- **🏥 Healthcare Data Management** - Comprehensive patient treatment record tracking
- **🔄 Automatic Conversion** - Smart time zone conversion to IST reporting standard
- **🎨 Modern UI/UX** - Responsive design with Tailwind CSS and intuitive interface
- **🔒 Enterprise Security** - Secure credential management and encrypted connections

---

## 🛠 Technology Stack

### Backend
- **FastAPI** - High-performance async web framework
- **Snowflake Connector** - Cloud data warehouse integration
- **Python-dotenv** - Environment configuration management

### Frontend
- **HTML5** - Modern semantic markup
- **Tailwind CSS** - Utility-first styling framework
- **Lucide Icons** - Beautiful consistent iconography
- **Vanilla JavaScript** - Lightweight, no framework overhead

---

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ Python 3.8 or higher installed
- ✅ Active Snowflake account with credentials
- ✅ pip package manager
- ✅ Git version control

---

## 🚀 Quick Start

### 1. Clone & Navigate

```bash
git clone https://github.com/Laxman-N/t0-global-ai-data-sync.git
cd t0-ai-agent-system
```

### 2. Set Up Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the `backend/` directory:

```env
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
```

> ⚠️ **Security Note:** Never commit `.env` files to version control

---

## 💾 Database Configuration

### Quick Setup

Run this SQL command in your Snowflake console:

```sql
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
```

> 📖 For detailed configuration, see `SNOWFLAKE_SETUP.md`

---

## 🎯 Running the Application

### Start Backend Server

```bash
cd backend
uvicorn main:app --reload --port 8001
```

> 💡 Using port 8001 to avoid conflicts with common port 8000 services

### Launch Frontend

Open `admin-dashboard/index.html` in your preferred web browser, or serve it using:

```bash
python -m http.server 8080
```

Then navigate to `http://localhost:8080/admin-dashboard/`

---

## 📡 API Reference

### Health & Status Check

**Endpoint:** `GET /report/summary`

**Description:** Retrieves connection status and database information

**Response Example:**
```json
{
    "status": "Success",
    "message": "Connection and query executed successfully.",
    "current_db_time": "2025-10-07 12:30:45",
    "connected_schema": "YOUR_DATABASE.YOUR_SCHEMA"
}
```

### Upload Treatment Data

**Endpoint:** `POST /data/upload`

**Description:** Uploads patient treatment records to Snowflake

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

**Response Example:**
```json
{
    "status": "success",
    "treatment_id": "TRT_12345",
    "ist_timestamp": "2025-10-07 20:00:00 IST"
}
```

---

## 🌐 Supported Time Zones

The system intelligently handles multiple time zones with automatic IST conversion:

| Region | Time Zones |
|--------|------------|
| **North America** | EST, CST, MST, PST |
| **Europe** | GMT/UTC, CET, EET |
| **Asia** | IST (Standard), GST, SGT, JST |
| **Oceania** | AEST, NZST |

All timestamps are normalized to **IST (Indian Standard Time)** for standardized reporting and analysis.

---

## 📁 Project Architecture

```
t0-ai-agent-system/
│
├── 📂 admin-dashboard/
│   └── 📄 index.html              # Main dashboard interface
│
├── 📂 backend/
│   ├── 📂 ai_agent/
│   │   └── 📄 time_sync_agent.py  # Time zone conversion logic
│   ├── 📄 main.py                 # FastAPI application entry
│   ├── 📄 config.py               # Configuration management
│   └── 📄 requirements.txt        # Python dependencies
│
├── 📄 .gitignore                  # Git exclusion rules
├── 📄 README.md                   # Project documentation
└── 📄 SNOWFLAKE_SETUP.md          # Database setup guide
```

---

## 🔐 Security Best Practices

### Files to Never Commit

The following files contain sensitive information and are automatically excluded:

- 🚫 `.env` - Database credentials and API keys
- 🚫 `rsa_key.p8` - Private authentication key
- 🚫 `rsa_key.pub` - Public authentication key
- 🚫 `*.log` - Application logs

> ✅ These are pre-configured in `.gitignore`

### Additional Recommendations

- Use environment-specific configuration files
- Implement role-based access control in Snowflake
- Enable MFA for all production accounts
- Regularly rotate credentials and keys
- Use HTTPS for all API communications

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Workflow

1. **Fork** the repository to your GitHub account
2. **Create** a feature branch
   ```bash
   git checkout -b feature/YourAmazingFeature
   ```
3. **Commit** your changes with descriptive messages
   ```bash
   git commit -m "feat: Add amazing new feature"
   ```
4. **Push** to your branch
   ```bash
   git push origin feature/YourAmazingFeature
   ```
5. **Open** a Pull Request with a detailed description

### Commit Convention

We follow semantic commit messages:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation updates
- `style:` Code formatting
- `refactor:` Code restructuring
- `test:` Test additions/updates
- `chore:` Maintenance tasks

---

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE.md](LICENSE.md) for full details.

---

## 💬 Support & Community

### Get Help

- 🐛 **Bug Reports:** [Open an Issue](https://github.com/Laxman-N/t0-global-ai-data-sync/issues)
- 💡 **Feature Requests:** [Start a Discussion](https://github.com/Laxman-N/t0-global-ai-data-sync/discussions)
- 📧 **Email:** support@yourdomain.com

### Stay Updated

- ⭐ Star the repository to show support
- 👀 Watch for updates and releases
- 🍴 Fork to create your own version

---

## 🙏 Acknowledgments

Special thanks to the incredible tools and teams behind:

- **Snowflake** - Cloud data warehouse platform
- **FastAPI** - Modern Python web framework
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide** - Beautiful icon library

---

## 🔄 Changelog

### Version 1.0.0 (Current)
- ✨ Initial release with core functionality
- 🌍 Multi-timezone support
- 📊 Real-time Snowflake integration
- 🎨 Modern responsive dashboard

---

<div align="center">

**Made with ❤️ for global healthcare data management**

[⬆ Back to Top](#-global-ai-data-sync-dashboard)

</div>