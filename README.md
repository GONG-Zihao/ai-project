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

### Option A · One-command API (SQLite)

```bash
cp .env.example .env
bash scripts/dev_quickstart.sh
```

The script installs core dependencies, switches to SQLite if no database is running, and starts FastAPI at <http://127.0.0.1:8000>. Swagger UI: `/docs`. Seeded tenant `default` with admin `admin / Admin@123`.

### Option B · Full stack (Docker compose)

```bash
docker compose -f infra/docker/docker-compose.dev.yml up --build
```

### Hooking up the Streamlit prototype

```bash
cd apps/streamlit
python -m pip install streamlit plotly pandas networkx pillow matplotlib
export API_BASE_URL=http://127.0.0.1:8000/api/v1
python -m streamlit run streamlit_app.py
```

Use tenant `default` plus backend credentials to unlock the new data-driven experience (错题本 / 学习建议 / 学习进度 / 学习成就 均直接来自 FastAPI)。

## 新增能力速览

- **后端 API 扩展**：`/analytics/*` 输出学习进度与成就；`/teacher/*` 提供班级管理、学情看板；`/learning/knowledge` 支持知识点维护。
- **AI 调度升级**：新增 `/qa/lesson-plan` 教师课堂方案生成；AI 答复统一带引用与安全标签。
- **前端对接**：Streamlit 页面改为调用 FastAPI，错题、建议、进度、成就全部实时同步后端。
- **运维体验**：新版 `.env.example` 覆盖常见场景（含 SQLite 快启）；`scripts/dev_quickstart.sh` 一键安装+启动。

## Status

Implementation continues to follow the upgrade roadmap documented in `AI_EDU_OPTIMIZATION_BLUEPRINT.md`.
