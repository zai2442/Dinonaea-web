# Backend System Specification

## 1. Overview
This document outlines the design and implementation details for the Dionaea Log Management Backend System. The system is built using Python (FastAPI), PostgreSQL, and Redis, focusing on security, scalability, and maintainability. It provides robust user management, data management capabilities, and granular permission control (RBAC).

## 2. Technology Stack
-   **Framework**: FastAPI (Python 3.11+)
-   **Database**: PostgreSQL 15+
-   **ORM**: SQLAlchemy / SQLModel
-   **Cache**: Redis (for permission caching)
-   **Validation**: Pydantic v2
-   **Authentication**: JWT (Access + Refresh Token)
-   **Migration**: Flyway (SQL-based migrations)
-   **Testing**: Pytest
-   **Documentation**: OpenAPI / Swagger 3.0

## 3. Architecture Design

### 3.1 Layered Architecture
-   **API Layer**: FastAPI Routers, Pydantic Schemas (DTOs), Middleware.
-   **Service Layer**: Business Logic, Transaction Management, Caching Logic.
-   **Repository Layer**: Database Access (SQLAlchemy), Data Transformation.
-   **Database Layer**: PostgreSQL Tables, Indexes, Constraints.

### 3.2 Security Architecture
-   **Authentication**: JWT-based stateless authentication.
    -   `accessToken`: Short-lived (e.g., 15 mins).
    -   `refreshToken`: Long-lived (e.g., 7 days), stored securely (HttpOnly cookie or secure storage).
-   **Authorization**: RBAC (Role-Based Access Control).
    -   User -> Roles -> Permissions.
    -   `@require_permission` decorator for fine-grained control.
    -   Redis caching for permission lookups (5-minute TTL).
-   **Data Protection**:
    -   Optimistic Locking (`version` field) for concurrent updates.
    -   Audit Logging for sensitive operations.

## 4. Database Schema Design

### 4.1 Common Fields (Base Model)
All business tables will include:
-   `id`: Primary Key (BigInt/UUID)
-   `create_by`: User ID (Foreign Key)
-   `create_time`: Timestamp
-   `update_by`: User ID (Foreign Key)
-   `update_time`: Timestamp
-   `version`: Integer (Optimistic Lock)
-   `deleted`: Boolean (0: Active, 1: Deleted)

### 4.2 Core Tables
-   **users**:
    -   `username` (Unique, Indexed)
    -   `email` (Unique, Indexed)
    -   `password_hash`
    -   `status` (Active/Disabled, Indexed)
    -   `last_login_time`
-   **roles**:
    -   `name` (Unique)
    -   `description`
    -   `code` (Unique Identifier, e.g., `admin`)
-   **permissions**:
    -   `code` (Unique, e.g., `user:add`)
    -   `description`
    -   `resource_type`
-   **user_roles**: Mapping table (User <-> Role).
-   **role_permissions**: Mapping table (Role <-> Permission).
-   **audit_log**:
    -   `user_id`
    -   `action` (e.g., `DELETE_USER`)
    -   `resource_id`
    -   `params` (JSON)
    -   `result` (Success/Fail)
    -   `ip_address`
    -   `timestamp`
-   **attack_logs** (Existing, Enhanced):
    -   `timestamp` (Indexed)
    -   `username` (Indexed)
    -   `source_ip` (Indexed)
    -   `password`
    -   `protocol` (e.g., ssh, ftp)
    -   `sensor_name`

## 5. Module Specifications

### 5.1 User Management
-   **Endpoints**:
    -   `POST /api/v1/auth/login`: Returns tokens.
    -   `POST /api/v1/auth/refresh`: Refreshes access token.
    -   `POST /api/v1/auth/logout`: Invalidates tokens.
    -   `POST /api/v1/users`: Create user (Admin only).
    -   `PUT /api/v1/users/{id}`: Update user.
    -   `DELETE /api/v1/users/{id}`: Soft delete, cascade cleanup logic.
    -   `GET /api/v1/users`: List with pagination, filters (username, email, role, status).
-   **Performance**: Query response <= 200ms for 100k users (requires proper indexing).

### 5.2 Data Management (Generic CRUD)
-   **Features**:
    -   Dynamic CRUD templates using SQLAlchemy.
    -   Field-level permission checks in Service layer.
    -   Advanced Filtering:
        -   `/api/v1/data/{resource}?filter=age:gt:18,name:like:John&sort=-created_time`
    -   **Export**:
        -   JSON export (StreamingResponse) for large datasets (up to 100k rows).
        -   Memory usage constrained to <= 500MB via chunked processing.
    -   **Batch Operations**:
        -   `DELETE /api/v1/data/{resource}/batch`: Transactional, max 1000 items.
        -   Rollback on any failure, returns specific error details.

### 5.3 Permission Control
-   **Implementation**:
    -   `PermissionDependency` (FastAPI dependency) checks Redis cache.
    -   Cache Key: `rbac:user:{user_id}:permissions`.
    -   Cache Invalidation: On Role/Permission update, clear relevant keys.
-   **Latency**: Check overhead <= 10ms.

## 6. Development Standards

### 6.1 API Standards
-   **URL Structure**: `/api/v1/{resource}/{id}`
-   **Response Format**:
    ```json
    {
        "code": 0,
        "msg": "success",
        "data": { ... }
    }
    ```
-   **Error Handling**:
    -   Global Exception Handler for `BusinessException`, `ValidationException`.
    -   Map to standard HTTP codes (400, 401, 403, 404, 500).

### 6.2 Code Quality
-   **Linting**: `flake8`, `black`, `isort`, `mypy`.
-   **Security Scan**: `bandit`.
-   **Tests**: `pytest` (Unit + Integration), `Postman` collections.
-   **Coverage**: Minimum 80%.

### 6.3 Documentation
-   **Swagger**: Auto-generated via FastAPI.
-   **Implementation Notes**: `DOCS/backend/IMPLEMENTATION_NOTES.md`.
-   **UML**: ER Diagram, Sequence Diagram (PlantUML).
