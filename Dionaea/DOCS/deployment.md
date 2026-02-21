# Deployment Guide

## Prerequisites
- Docker & Docker Compose
- Python 3.9+
- Redis (provided via docker-compose)

## Installation

1. **Start Services**
   ```bash
   cd Dinonaea-web/Dionaea
   sudo docker-compose up -d
   ```

2. **Backend Setup**
   ```bash
   cd Dinonaea-web/Dionaea
   python3 -m venv backend/venv
   source backend/venv/bin/activate
   pip install -r backend/requirements.txt
   # Install additional dependencies if missing
   pip install redis uvicorn
   ```

3. **Database Initialization**
   ```bash
   # Initialize tables
   PYTHONPATH=backend python backend/ingestor.py
   ```

4. **Run Backend Server**
   ```bash
   PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port 8001
   ```

5. **Frontend Setup**
   - Serve `frontend_login_demo` via Nginx or any static file server.
   - Update `CONFIG.API_BASE` in `assets/js/app.js` and `assets/js/dashboard.js` if backend URL differs.

## Scheduled Tasks
Add the following to crontab for log monitoring:
```cron
*/5 * * * * /bin/bash /path/to/Dionaea/Check.sh
```

## Configuration
- **Environment Variables**: Create `.env` in `backend/` (see `backend/app/core/config.py` for defaults).
- **Log Path**: Ensure `Dionaea.log` exists at `/opt/Dionaea.log` or update `Check.sh` and `ingestor.py`.

## Verification
- Access Dashboard: `http://localhost:8000/dashboard.html` (if served on 8000)
- API Docs: `http://localhost:8001/docs`
