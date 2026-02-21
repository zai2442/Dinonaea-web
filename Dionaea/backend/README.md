# Dionaea Log Manager Backend

This is the backend service for Dionaea Log Manager, built with FastAPI, PostgreSQL, and Redis.

## Prerequisites
-   Python 3.11+
-   PostgreSQL 15+
-   Redis 7+

## Setup

1.  **Install Dependencies**:
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

2.  **Configure Environment**:
    -   Create a `.env` file in `backend/` or set environment variables.
    -   `DATABASE_URL=postgresql://user:pass@localhost:5432/db_name`
    -   `REDIS_URL=redis://localhost:6379/0`
    -   `SECRET_KEY=your_secret_key`

3.  **Database Migration**:
    -   The application automatically creates tables on startup (dev mode).
    -   For production, use the SQL scripts in `DOCS/db/migration/`.

4.  **Run Application**:
    ```bash
    python main.py
    # or
    uvicorn app.main:app --reload
    ```

## API Documentation
-   Swagger UI: http://localhost:8001/docs
-   ReDoc: http://localhost:8001/redoc

## Features
-   **User Management**: JWT Auth, RBAC, User CRUD.
-   **Data Management**: Generic CRUD, Advanced Filtering, Export.
-   **Security**: Optimistic Locking, Audit Logs.

## Testing
```bash
pytest
```
