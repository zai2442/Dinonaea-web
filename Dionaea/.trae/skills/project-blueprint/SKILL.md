---
name: project-blueprint
description: "Create comprehensive software project documentation including Product Requirements Documents (PRD), Technical Specifications (TSD), and Data Model & API Documentation (DMA). Use when (1) starting a new software project or feature, (2) the user requests project planning, design documents, or technical specifications, (3) architecting systems that need formal documentation, or (4) the user asks to create PRD, TSD, DMA, or similar project blueprints. Now enhanced with persistent planning and resilient workflows."
---

# Project Blueprint

Generate high-quality software project documentation that transforms ideas into actionable development plans. This skill creates three essential documents that define what to build (PRD), how to build it (TSD), and the data/API structure (DMA).

## 🧠 Persistent Working Memory

When starting a complex blueprinting task, you MUST initialize persistent working memory in the project directory. This ensures resilience against context loss.

1.  **Create `task_plan.md`** — Track documentation phases, milestones, and status.
2.  **Create `findings.md`** — Store research, requirement discoveries, and tech stack options.
3.  **Create `progress.md`** — Log session activities and decision history.

### The 2-Action Rule
**After every 2 requirement-gathering or research operations (search, read, etc.), IMMEDIATELY save key findings to `findings.md`.** This prevents loss of critical project details.

## 🛡️ Resilient Workflow (3-Strike Protocol)

Blueprinting often involves technical research that can fail. Use this protocol:
- **ATTEMPT 1**: Diagnose and fix specific issues in the spec or design.
- **ATTEMPT 2**: Try an alternative architecture or technology.
- **ATTEMPT 3**: Re-read the PRD and rethink the design approach.
- **AFTER 3 FAILURES**: Escalate architectural blockers to the user.

## Core Documentation Framework

Generate these three documents in sequence:

1. **PRD (Product Requirements Document)** — Defines WHAT and WHY. Template: [references/prd.md](references/prd.md)
2. **TSD (Technical Specification Document)** — Defines HOW. Template: [references/tsd.md](references/tsd.md)
3. **DMA (Data Model & API Documentation)** — Defines STRUCTURE. Template: [references/dma.md](references/dma.md)

## Workflow

### Phase 0: Initialization & Planning
- Initialize `task_plan.md` with PRD, TSD, and DMA phases.
- Start `findings.md` with any initial user prompts.

### Phase 1: Discovery & Requirements (PRD)

**1. Understand the Vision**
Ask clarifying questions before writing. Document answers in `findings.md`.
- What problem does this solve? Who are the users?
- What are the top 3-5 must-have features?
- Constraints (budget, timeline, existing tech)?

**2. Generate PRD**
Create `DOCS/PRD.md` using [references/prd.md](references/prd.md).
- Prioritize functional requirements (P0/P1/P2).
- Define clear success metrics.

**3. Review & Update Plan**
Share PRD with user. Update `task_plan.md` once PRD is approved.

### Phase 2: Technical Design (TSD)

**1. Gather Technical Context**
Identify tech preferences and infrastructure constraints. Store in `findings.md`.

**2. Generate TSD**
Create `DOCS/TSD.md` using [references/tsd.md](references/tsd.md).
- Use Mermaid for system architecture.
- Justify key design decisions (Rationale vs consequences).

**3. Review & Update Plan**
Get architecture approval. Update `task_plan.md`.

### Phase 3: Data & API Design (DMA)

**1. Identify Data Requirements**
Determine entities, relationships, and API needs from the TSD and PRD.

**2. Generate DMA**
Create `DOCS/DMA.md` using [references/dma.md](references/dma.md).
- ER diagrams (Mermaid).
- Schema details and API endpoints with request/response examples.

## Best Practices

**Use Mermaid Diagrams**
- Mandatory for architecture (TSD) and ER models (DMA).

**Be Specific, Not Generic**
- Define exact versions (e.g., "Node.js 20 LTS" instead of "Node.js").

**Link Documents**
- Cross-reference PRD requirements in TSD rationale.
- Map TSD services to DMA API endpoints.

**Update Planning Files**
- Mark phases complete in `task_plan.md` as files are finalized.

## Output Location

```
DOCS/
├── PRD.md
├── TSD.md
└── DMA.md
```