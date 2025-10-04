# AI Education Platform (Next-Gen)

This repository houses the next-generation "AI+教育教学" platform. It follows the blueprint defined in `AI_EDU_OPTIMIZATION_BLUEPRINT.md` and implements a modular architecture ready for classroom-scale deployments.

## Repository Layout

```
.
├─ apps/                # Frontend applications (web, admin, legacy streamlit)
├─ services/            # Backend microservices (api, ai, retrieval, worker)
├─ packages/            # Shared Python packages and SDKs
├─ infra/               # Deployment assets (docker, k8s, migrations)
├─ docs/                # Documentation (legacy README, blueprints, specs)
├─ configs/             # Centralised configuration templates
├─ requirements/        # Dependency manifests
├─ tests/               # Automated tests (unit, integration, e2e stubs)
└─ AI_EDU_OPTIMIZATION_BLUEPRINT.md
```

## Quickstart

1. Copy `.env.example` to `.env` and adjust secrets.
2. Install dependencies: `make install-all`
3. Launch local stack: `make dev`
4. Access FastAPI docs at `http://localhost:8000/docs` (after Phase 1 setup)

## Status

Implementation tracks the phases defined in the blueprint. See `docs/CHANGELOG.md` (to be created) for progress updates.
