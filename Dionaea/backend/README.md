# Dionaea Log Ingestion Prototype

This prototype provides a backend system to ingest, store, and query Dionaea honeypot logs.

## Prerequisites

- Docker & Docker Compose
- Python 3.11+

## Quick Start

### 1. Start Database

```bash
# In the root directory (d:\dinoaea-web\Dionaea)
docker-compose up -d
```

This starts a PostgreSQL 15 container.

### 2. Setup Backend Environment

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure & Run Ingestion

Create a dummy log file for testing (or point to your real log):

```bash
# Create logs directory if not exists
mkdir ../logs
echo "Wed, 18 Feb 2026 20:08:41  Username:admin Password:123 ipaddr:192.168.1.100" > ../logs/Dionaea.log
```

Run the ingestor:

```bash
# Set environment variable for log path
set DIONAEA_LOG_PATH=../logs/Dionaea.log
# Set DB URL if changed in docker-compose
set DATABASE_URL=postgresql://dionaea_user:dionaea_pass@localhost:5432/dionaea_db

python ingestor.py
```

The script will read the log file and insert records into the database.

### 4. Run Query API

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

Access the API docs at: http://127.0.0.1:8000/docs

## API Endpoints

- `GET /logs`: List logs with filtering (username, source_ip, dates)
- `GET /logs/stats`: Basic statistics
- `GET /`: Health check

### Example API Usage

**Get logs from specific IP:**
```bash
curl "http://127.0.0.1:8000/logs?source_ip=127.0.0.1"
```

**Get logs for a username:**
```bash
curl "http://127.0.0.1:8000/logs?username=admin"
```

## Database Schema

Table `attack_logs`:
- `id`: PK
- `timestamp`: DateTime (Indexed)
- `username`: String (Indexed)
- `password`: String
- `source_ip`: String (Indexed)
- `created_at`: DateTime

### Example SQL Queries

Connect to DB:
```bash
docker exec -it dionaea_db psql -U dionaea_user -d dionaea_db
```

**Top 5 Attackers:**
```sql
SELECT source_ip, COUNT(*) as count 
FROM attack_logs 
GROUP BY source_ip 
ORDER BY count DESC 
LIMIT 5;
```

**Attacks per Day:**
```sql
SELECT date_trunc('day', timestamp) as day, COUNT(*) 
FROM attack_logs 
GROUP BY day 
ORDER BY day DESC;
```
