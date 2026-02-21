# Test Report: Dionaea Log Ingestion & API

## 1. Overview
This report verifies the implementation of the real-time log ingestion daemon and the new RESTful API for querying attack logs.

## 2. Ingestion Test
**Objective**: Verify that `ingestor.py` monitors `/tmp/Dionaea` directory and ingests new logs in real-time.

**Procedure**:
1. Started `ingestor.py` service.
2. Created `/tmp/Dionaea/test.log` with sample attack data.
3. Verified logs were processed.

**Result**:
- Service detected new file: `/tmp/Dionaea/test.log`.
- Ingested 2 new log entries into PostgreSQL database.
- Data includes new fields: `raw_log` and `attack_type` (defaulted to 'smb' as per current logic).

## 3. API Test
**Objective**: Verify `GET /api/v1/logs` endpoint supports filtering.

**Procedure**:
- Ran `pytest backend/tests/test_logs_api.py`.
- Tests covered:
  - `test_get_logs`: Fetch all logs.
  - `test_get_logs_filter_attack_type`: Filter by `attack_type=smb`.
  - `test_get_logs_filter_time`: Filter by time range (future time returns empty).

**Result**:
```
backend/tests/test_logs_api.py ...                                      [100%]
3 passed in 0.12s
```
All tests passed successfully.

## 4. Database Migration
- Added `raw_log` (TEXT) and `attack_type` (VARCHAR) columns to `attack_logs` table via `backend/migrations/add_column_attack_logs.sql`.
- Validated via successful insertion and query.
