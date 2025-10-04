# Architecture Overview

This repository implements the layered design defined in `AI_EDU_OPTIMIZATION_BLUEPRINT.md`.

- **Apps**: Frontend code. `apps/streamlit` retains the legacy prototype but now integrates with the new API when `API_BASE_URL` is configured. Slots are prepared for `apps/web` (Next.js) and `apps/admin`.
- **Services**:
  - `services/api`: FastAPI application providing authentication, user management, AI QA endpoints (including `/qa/lesson-plan` for teachers), learning analytics, teacher-facing dashboards, and audit logging. It persists data to PostgreSQL via SQLAlchemy models.
  - `services/ai`: LLM orchestration, prompt templating, safety checks, and RAG helpers.
  - `services/retrieval`: Vector store wrapper (Qdrant) and document chunking utilities.
  - `services/worker`: Celery tasks for OCR, retrieval indexing, and background jobs.
- **Packages**: Reusable Python packages (`packages/common`) with configuration handling.
- **Infra**: Docker compose stack, dockerfiles, and migration stubs.
- **Requirements**: Dependency manifests separated by concern.

## Backend Highlights

- JWT-based auth with tenant awareness and RBAC helpers.
- Entities: tenants, users, classrooms, problems, mistakes, study sessions, knowledge points, recommendations, audit events.
- AI facade connects to DeepSeek/OpenAI/Mock providers with automatic fallbacks and basic safety checks.
- Learning analytics produce personalized plans, mastery estimates, and class-wide dashboards (`/analytics/*`, `/teacher/*`).
- Audit logging for critical actions (QA requests, mistake creation, study sessions).

## Next Steps

- Implement Alembic migrations and unify database deployments.
- Build out Next.js frontend and teacher console.
- Extend observability (OpenTelemetry, SLO dashboards) and compliance workflows.
- Harden AI evaluation (structured outputs, rubric baselines, automated regression tests).
