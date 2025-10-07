Deployment Guide: Global Data Sync
This document outlines the steps necessary to deploy the Global Data Sync application, which consists of a Python FastAPI backend and a static HTML/JS admin dashboard.

1. Prerequisites
Ensure you have the following services and tools ready:

Python 3.8+

Git

Docker (Recommended for containerized deployment)

Snowflake Account with necessary database, warehouse, and user credentials.

Environment variables set up according to backend/.env.example.

2. Snowflake Setup
Before deployment, ensure your Snowflake environment is configured as described in the SNOWFLAKE_SETUP.md guide.

3. Backend Deployment (FastAPI)
The backend handles all data connection, synchronization, and API requests.

Option A: Local (Development)
Navigate to the backend directory:

cd backend

Install dependencies:

pip install -r requirements.txt

Set your environment variables by creating a file named .env and filling it with the required credentials from .env.example.

Run the application using Uvicorn (or your chosen ASGI server):

uvicorn main:app --reload --host 0.0.0.0 --port 8001

Option B: Docker (Production)
(Assuming a Dockerfile exists or will be created for the backend)

Build the Docker image from the project root:

docker build -t global-data-sync-backend:latest .

Run the container, exposing the backend port (default 8001):

docker run -d -p 8001:8001 --env-file ./backend/.env global-data-sync-backend:latest

4. Frontend Deployment (Admin Dashboard)
The frontend is a static HTML/JS dashboard located in admin-dashboard/index.html.

Deployment
This can be hosted by any static file server (e.g., Nginx, Apache, or cloud storage like S3/GCS).

Copy the contents of the admin-dashboard/ folder to your static hosting service.

Ensure that the frontend is configured to communicate with your deployed backend URL (e.g., https://api.yourdomain.com).

Troubleshooting
Connection Errors: Double-check your Snowflake credentials in the .env file. Ensure the backend host/port is accessible from the client.

Missing Libraries: If running locally, ensure all dependencies are installed with pip install -r requirements.txt.