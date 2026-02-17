# Technical Specification Document (TSD)

## 1. System Architecture

### 1.1 Overview
The system follows a modern decoupled architecture:
- **Frontend**: Single Page Application (SPA) using Vue 3.
- **Backend**: RESTful API using FastAPI (Python).
- **Database**: PostgreSQL for relational data, Redis for caching and queues.
- **Data Pipeline**: Log parsing agent -> Celery Task -> Database.

### 1.2 Tech Stack

| Component | Technology | Version |
| :--- | :--- | :--- |
| **Language** | Python | 3.11 |
| **Web Framework** | FastAPI | Latest |
| **Frontend Framework** | Vue.js | 3.3 |
| **Language (FE)** | TypeScript | 5.x |
| **State Management** | Pinia | Latest |
| **UI Component Lib** | Element Plus | Latest |
| **Database** | PostgreSQL | 15 |
| **Task Queue** | Celery + Redis | Latest |
| **Visualization** | ECharts | 5.x |
| **Containerization** | Docker Compose | Latest |

## 2. Component Design

### 2.1 Backend (FastAPI)
- **Auth Module**: Handles JWT issuance, verification, and refresh. Implements OAuth2PasswordBearer.
- **User Module**: CRUD for Users and Roles. Enforces RBAC via dependencies.
- **Honeypot Module**:
    - `LogIngestor`: Background service/task to read/receive logs.
    - `DataAPI`: Endpoints for querying logs with filtering/sorting.
    - `WebSocketManager`: Broadcasts real-time events to connected clients.
- **Config Module**: Manages system settings and alert rules.

### 2.2 Frontend (Vue 3)
- **Layout**: MainLayout (Sidebar + Header + Content).
- **Views**:
    - `src/views/user/`: User management pages.
    - `src/views/honeypot/`: Dashboard and Log tables.
    - `src/views/dashboard/`: Aggregate charts.
- **Components**:
    - `CommonChart`: Reusable ECharts wrapper.
    - `DataTable`: standardized table with pagination/sorting.

### 2.3 Data Pipeline
1.  **Source**: `web_dionaea` writes to `/tmp/Dionaea.log` (or similar).
2.  **Collection**: A file watcher (or Filebeat) sends lines to the Backend or a Message Queue.
3.  **Processing**: Celery worker parses the log line (Regex/JSON), enriches it (GeoIP), and saves to PostgreSQL `attack_logs`.
4.  **Notification**: If alert rules match, trigger notification. Push to WebSocket.

## 3. Infrastructure & Deployment

### 3.1 Docker Composition
- `backend`: FastAPI app (uvicorn).
- `frontend`: Nginx serving built static files.
- `db`: PostgreSQL 15.
- `redis`: Redis 7.
- `worker`: Celery worker for log processing.

### 3.2 CI/CD
- **GitHub Actions**:
    - Linting (Black, ESLint).
    - Testing (Pytest, Jest).
    - Build & Push Docker images.

## 4. Security Design
- **Password Hashing**: bcrypt or Argon2.
- **Rate Limiting**: `slowapi` or Redis-based limiter on API endpoints.
- **Input Validation**: Pydantic models for all incoming data.
- **CORS**: Restricted to allowed origins.
