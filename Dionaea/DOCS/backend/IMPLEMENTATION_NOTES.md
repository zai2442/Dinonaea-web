# Implementation Notes - Log Statistics Module

## Overview
This module adds Dionaea honeypot log visualization and statistics to the dashboard. It ingests logs from a file, stores them in the database, and provides RESTful APIs for the frontend to display charts and tables.

## Components

### 1. Backend (FastAPI)
- **Model**: `AttackLog` (SQLAlchemy) in `app/models/attack_log.py`.
- **Schema**: `AttackLog`, `AttackLogStats` (Pydantic) in `app/schemas/attack_log.py`.
- **Service**: `AttackLogService` in `app/services/attack_log_service.py`.
    - Handles data retrieval and statistics calculation.
    - Uses Redis for caching statistics (10 minutes TTL).
- **API**: `app/api/v1/data.py`.
    - `GET /data/logs`: Paginated log list with filtering.
    - `GET /data/stats/charts`: Top IPs, Usernames, Passwords for charts.
    - `GET /data/stats/summary`: Summary stats (compatible with shell script output).
    - `POST /data/refresh`: Force refresh of statistics cache.

### 2. Data Ingestion
- **Script**: `backend/ingestor.py`
- **Function**: Reads `Dionaea.log` (path configurable via `DIONAEA_LOG_PATH`, default `/opt/Dionaea.log`).
- **Parsing**: Regex-based parsing of timestamp, username, password, IP.
- **Deduplication**: Simple check against existing records to avoid duplicates.

### 3. Frontend (Vanilla JS + ECharts)
- **Dashboard**: `dashboard.html` updated with "System Monitoring" and "Data Statistics" views.
- **Logic**: `assets/js/dashboard.js` handles data fetching and ECharts rendering.
- **Visuals**:
    - Bar Chart: Top 10 Attacker IPs.
    - Pie Chart: Top 5 Usernames.
    - Word Cloud: Top 20 Passwords.
    - Log Table: Paginated view of attack logs.

### 4. Integration
- **Check.sh**: Monitoring script (cron job).
    - Detects changes in `Dionaea.log` using MD5.
    - Triggers `Login_statistics.sh`.
    - Triggers backend cache refresh via `backend/scripts/refresh_cache.py`.

## Configuration
- **Redis**: Required for caching. Configured in `docker-compose.yml`.
- **Database**: SQLite (dev) or Postgres (prod).
- **Log Path**: Set `DIONAEA_LOG_PATH` environment variable.

## Testing
- Unit tests in `backend/tests/test_data_api.py`.
- Manual verification via `Check.sh` execution.
