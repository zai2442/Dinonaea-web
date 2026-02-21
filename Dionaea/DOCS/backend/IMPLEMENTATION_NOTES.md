# Implementation Notes

## 1. Technical Stack
-   **Framework**: FastAPI 0.129.0
-   **ORM**: SQLAlchemy 2.0.46
-   **Database**: PostgreSQL 15+
-   **Cache**: Redis 7.2.0 (Client: redis-py)
-   **Auth**: JWT (python-jose) + RBAC

## 2. Key Algorithms & Strategies

### 2.1 Permission Caching
-   **Strategy**: Redis key `rbac:user:{id}:permissions`.
-   **Invalidation**: When a Role or Permission is updated, we invalidate all related user keys or use a versioning scheme. Currently, we use a simple TTL (5 mins).

### 2.2 Pagination & Performance
-   **Optimization**:
    -   Used `Select(func.count())` for efficient counting.
    -   Indexed high-cardinality fields (`username`, `email`, `timestamp`).
    -   Used `offset/limit` pagination.
    -   For export, we use `StreamingResponse` (to be implemented fully) to avoid memory spikes.

### 2.3 Concurrency Control
-   **Optimistic Locking**:
    -   Each update checks `version` field.
    -   If `db_version != request_version`, throw 409 Conflict.
    -   Ensures no lost updates.

## 3. Challenges & Solutions

### 3.1 Circular Imports
-   **Problem**: `User` model needs `Role`, `Role` needs `User`.
-   **Solution**: Used `TYPE_CHECKING` imports and string references in `relationship()`.

### 3.2 Dynamic Filtering
-   **Problem**: Generic CRUD needs flexible filters.
-   **Solution**: Implemented a parser for `field:op:value` syntax (e.g., `age:gt:18`) in `GenericService`.

## 4. Performance Benchmarks (Projected)
-   **User List (100k rows)**: < 200ms with index.
-   **Login**: < 50ms.
-   **Throughput**: Expected ~1000 TPS on standard hardware.

## 5. Next Steps
-   Implement full streaming for JSON export.
-   Add more unit tests.
-   Set up CI/CD pipeline.
