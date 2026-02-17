# Project Documentation

This directory contains the complete development documentation for the `dinoaea-web` secondary development project.

## Documents

- **[Product Requirements Document (PRD)](PRD.md)**: Defines the project background, goals, user roles, and functional requirements.
- **[Technical Specification Document (TSD)](TSD.md)**: Details the system architecture, technology stack, component design, and infrastructure.
- **[Data Model & API Documentation (DMA)](DMA.md)**: Contains the Database ER diagram, Table definitions, and API specifications.
- **[Iteration Plan](ITERATION_PLAN.md)**: Breakdown of the development into 5 Sprints with specific tasks.
- **[UI/UX Standards](UI_UX.md)**: Detailed frontend design specifications (Colors, Fonts, Layouts).
- **[Testing Strategy](TESTING.md)**: Comprehensive testing plan including Unit, Integration, Performance, and Security testing.

## Quick Start (Proposed)

1.  **Backend Setup**:
    ```bash
    cd backend
    pip install -r requirements.txt
    docker-compose up -d db redis
    uvicorn main:app --reload
    ```

2.  **Frontend Setup**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

3.  **Documentation**:
    Refer to `PRD.md` for feature definitions and `DMA.md` for API usage.
