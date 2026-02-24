# Node Status Monitoring and Management Module

## Overview
This module provides real-time monitoring and management of Dionaea honeypot nodes. It includes a backend API for node registration and status reporting, a background monitoring service, and a frontend dashboard for visualization.

## Features
- **Real-time Monitoring**: Checks node status (Online/Offline) via ICMP Ping and Heartbeat.
- **Node Management**: Add, Edit, Delete nodes with IP validation.
- **Visualization**: Dashboard with status counters, list view, and statistical charts (Status Distribution, Grouping).
- **Alerting**: Supports WebSocket-based real-time alerts for offline nodes or high CPU usage (>80%).
- **History**: Records status changes and CPU usage history.

## Architecture
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (SQLAlchemy models: `Node`, `NodeHistory`)
- **Frontend**: Vanilla JS + Tailwind CSS + ECharts
- **Communication**: REST API for management, WebSocket for real-time updates.

## API Documentation

The full API documentation is available at `/docs` (Swagger UI). Key endpoints:

### Nodes
- `GET /api/v1/nodes/`: List all nodes (supports filtering by group/status).
- `POST /api/v1/nodes/`: Register a new node.
- `GET /api/v1/nodes/{id}`: Get node details.
- `PUT /api/v1/nodes/{id}`: Update node details.
- `DELETE /api/v1/nodes/{id}`: Remove a node.

### Monitoring
- `POST /api/v1/nodes/{id}/status`: Report node status (Heartbeat).
    - Payload: `{"status": "online", "cpu_usage": 45.0, "cpu_usage_detail": "..."}`
- `WS /api/v1/nodes/ws`: WebSocket endpoint for real-time updates.

## Deployment Guide

### Prerequisites
- Python 3.9+
- PostgreSQL
- Redis (optional, for future extensions)

### Installation
1.  **Database Migration**:
    The system automatically creates tables on startup. If you are upgrading from a version without the Nodes module, ensure the `nodes` and `node_history` tables are created.

2.  **Dependencies**:
    Ensure `ping` command is available on the server for ICMP monitoring.
    ```bash
    sudo apt-get install iputils-ping
    ```

3.  **Configuration**:
    No additional configuration is required. The monitor service starts automatically with the backend.

### Configuration Hot Reload
The system supports configuration updates via the API. Modifying node settings (IP, Name, Group) takes effect immediately for the monitoring service on the next cycle (60s interval).

## Testing
Run the unit tests to verify the module:
```bash
pytest tests/test_nodes.py
```
Expected output: 4 passed.

## Usage
1.  Log in to the Dashboard.
2.  Navigate to **System Settings** (系统设置) in the sidebar.
3.  Click **Add Node** to register a new honeypot node.
4.  The system will automatically ping the node every 60 seconds.
5.  View real-time status and CPU usage in the table and charts.
