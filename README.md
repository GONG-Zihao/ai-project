# AI+教育教学 平台（Next‑Gen）

面向课堂与自习场景的 AI 原生个性化学习平台。仓库采用多服务模块化架构，内置 API、AI 调度、检索（RAG）、异步任务，以及一个可对接后端的 Streamlit 原型应用。

推荐运行环境：Python 3.11（CI 使用），macOS/Linux/Windows，Docker（可选）。

— 关键入口：`services/api/src/main.py` 启动 FastAPI 后端（uvicorn 运行）；`apps/streamlit/streamlit_app.py` 为前端原型。


## 目录结构

```
.
├─ apps/
│  └─ streamlit/                 # 旧版原型（已支持对接新后端）
│     ├─ streamlit_app.py        # 主入口
│     ├─ api_client.py           # 调用后端 REST 的异步客户端
│     ├─ ai_core.py              # 本地答疑/知识图谱与 OCR（可选依赖）
│     ├─ pages/                  # 子页面（学习社区、学习计划、知识图谱、数据分析、成就）
│     └─ data/ assets/           # 本地示例数据与资源
├─ services/
│  ├─ api/                       # FastAPI 应用（多租户、鉴权、学习分析等）
│  │  └─ src/
│  │     ├─ main.py              # 应用入口（路由注册、CORS、安全头、中间件、启动钩子）
│  │     ├─ api/ v1/             # 路由模块（auth/users/mistakes/qa/learning/teacher/analytics 等）
│  │     ├─ core/                # 配置、日志、加密（JWT、密码哈希）
│  │     ├─ db/ models/          # SQLAlchemy ORM 模型
│  │     ├─ repositories/        # 数据访问层（CRUD/查询）
│  │     ├─ schemas/             # Pydantic 输入输出模型
│  │     └─ services/            # 领域服务（学习分析、AI 封装）
│  ├─ ai/                        # LLM 调度、提示词模板、安全评估、RAG 客户端
│  │  └─ src/
│  │     ├─ orchestrator.py      # 多提供商编排（DeepSeek/OpenAI/Mock）
│  │     ├─ providers/           # 各 LLM Provider 封装
│  │     ├─ pipelines/qa.py      # 问答管线（检索→提示→生成→安全）
│  │     ├─ retrieval_client.py  # 向量检索客户端（Qdrant，可选）
│  │     └─ prompting/           # 提示模板与学科规则
│  ├─ retrieval/                 # 向量库与文档切分工具
│  │  └─ src/ (vector_store.py, documents.py)
│  └─ worker/                    # Celery 异步任务（OCR、检索入库）
│     └─ src/ (celery_app.py, tasks/ocr.py, tasks/retrieval.py)
├─ packages/
│  ├─ common/src/ai_edu_core/    # 通用配置（Pydantic Settings）
│  └─ clients/python/            # SDK 占位（后续扩展）
├─ infra/
│  ├─ docker/                    # 开发用 Compose 与 Dockerfiles
│  └─ migrations/                # Alembic 迁移（占位）
├─ configs/                      # 日志等集中配置
├─ requirements/                 # 依赖清单（base/ai/worker/dev/all）
├─ tests/                        # 单元测试（orchestrator、learning plan）
├─ scripts/                      # 开发脚本（SQLite 快启）
├─ .github/workflows/ci.yml      # CI（Lint + Test + Postgres 服务）
├─ .env.example                  # 环境变量模板
├─ pyproject.toml                # 工程与工具链配置
└─ README.md
```

补充：更详细的架构说明参见 `docs/ARCHITECTURE.md`。


## 快速开始

### 方案 A：一键本地后端（SQLite）

```bash
cp .env.example .env
bash scripts/dev_quickstart.sh
```

说明：脚本会安装基础依赖，默认使用 SQLite 启动后端，监听 <http://127.0.0.1:8000>，Swagger UI 在 `/docs`。首次启动会自动建表并创建默认租户与管理员账号（tenant: `default`，用户：`admin`，密码：`Admin@123`）。

等效手动方式：

```bash
python -m pip install -r requirements/base.txt -e packages/common aiosqlite
export DATABASE_URL=sqlite+aiosqlite:///./dev.db
export SYNC_DATABASE_URL=sqlite:///./dev.db
uvicorn services.api.src.main:app --reload --port 8000
```

### 方案 B：完整本地栈（Docker Compose）

```bash
docker compose -f infra/docker/docker-compose.dev.yml up --build
```

该栈包含：`api`、`worker`、`postgres`、`redis`、`qdrant`、`minio`，并挂载本地代码目录用于热更新。

### 对接 Streamlit 原型

```bash
cd apps/streamlit
python -m pip install streamlit plotly pandas networkx pillow matplotlib httpx
export API_BASE_URL=http://127.0.0.1:8000/api/v1
streamlit run streamlit_app.py
```

登录后（租户：`default`），即可在原型中使用后端的“错题本 / 学习建议 / 学习进度 / 学习成就”等能力。


## 配置与环境

集中配置位于 `packages/common/src/ai_edu_core/config.py`，通过 Pydantic Settings 读取 `.env`（大小写不敏感）。可用变量见 `.env.example`：

- 核心：`APP_ENV`、`APP_DEBUG`、`SECRET_KEY`、`ACCESS_TOKEN_EXPIRE_MINUTES`、`ALLOWED_ORIGINS`
- 数据库：`DATABASE_URL`、`SYNC_DATABASE_URL`（支持 SQLite / Postgres）
- Redis：`REDIS_URL`
- 向量库：`QDRANT_URL`、`QDRANT_API_KEY`
- 对象存储：`S3_ENDPOINT_URL`、`S3_ACCESS_KEY`、`S3_SECRET_KEY`、`S3_BUCKET`
- AI 提供商：`OPENAI_API_KEY`、`DEEPSEEK_API_KEY`、`AZURE_OPENAI_*`、`DEFAULT_LLM_PROVIDER`、`DEFAULT_LLM_MODEL`
- 特性开关：`enable_mock_ai`（默认启用 Mock 以便本地无 Key 也可运行）、`enable_local_llm`

日志配置位于 `configs/logging.json`，后端启动时自动加载（Debug 模式会下调控制台级别）。


## 后端服务概览（FastAPI）

- 应用入口：`services/api/src/main.py`，注册 CORS、安全响应头、中间件与启动钩子（建表、默认管理员创建）。
- 配置复用：`services/api/src/core/config.py` 直接复用 `ai_edu_core.settings`。
- 数据访问：`services/api/src/db/models/*` + `services/api/src/repositories/*`。
- 认证与权限：JWT（`/auth/token`、`/auth/login`），多租户感知，`require_roles` 装饰器控制教师/管理员权限。
- 领域能力：
  - AI 问答/教案：`/qa/ask`、`/qa/lesson-plan`
  - 学习记录：`/mistakes`、`/study-sessions`
  - 学习适配：`/learning/plan`、`/learning/knowledge`（支持知识点增改）
  - 教师端：`/teacher/classrooms*`（建班、选课、看板）
  - 分析总览：`/analytics/progress`、`/analytics/achievements`

路由根前缀为 `/api/v1`（见 `services/api/src/api/v1/__init__.py`）。

示例：获取 Token、调用问答

```bash
# 1) 登录获取 Token（默认租户 default）
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H 'content-type: application/json' \
  -d '{"tenant_slug":"default","username":"admin","password":"Admin@123"}'

# 2) 携带 Token 调用问答
curl -X POST http://127.0.0.1:8000/api/v1/qa/ask \
  -H 'authorization: Bearer <access_token>' \
  -H 'content-type: application/json' \
  -d '{"question":"牛顿第二定律是什么？","subject":"物理"}'
```


## AI 调度与 RAG

- 调度器：`services/ai/src/orchestrator.py` 支持 DeepSeek、OpenAI 与 Mock 提供商；当主提供商失败且未强制 Mock 时自动回退（`tests/unit/test_orchestrator.py` 覆盖）。
- 提示与安全：`services/ai/src/prompting/templates.py` 定义学科系统提示与主提示模板；`services/ai/src/safety.py` 对生成内容进行基础安全评估（标注在返回 metadata）。
- RAG：`services/ai/src/retrieval_client.py` 调用编排器生成向量→`services/retrieval/src/vector_store.py` 查询 Qdrant；未配置向量库或启用 Mock 时返回示例上下文。文档切分在 `services/retrieval/src/documents.py`。
- 课件/知识库入库：可通过 Celery 任务 `services.worker.src.tasks.retrieval.index_materials` 批量索引本地文本资料。


## 异步任务（Celery）

- 应用：`services/worker/src/celery_app.py`，Broker/Backend 默认走 Redis。
- 任务：
  - OCR：`services/worker/src/tasks/ocr.py`（可选依赖 PaddleOCR，Windows 默认跳过）
  - 检索入库：`services/worker/src/tasks/retrieval.py`
- 本地手动启动（非 Docker）：

```bash
celery -A services.worker.src.celery_app:celery_app worker -l info
```


## 数据模型（简述）

- 多租户：`tenants`
- 用户及角色：`users`（Student/Teacher/Guardian/Admin）
- 班级与选课：`classrooms`、`enrollments`
- 题目与错题：`problems`、`mistakes`
- 学习过程：`study_sessions`、`interactions`
- 知识点与建议：`knowledge_points`、`recommendations`
- 审计日志：`audit_events`

关系定义见 `services/api/src/db/models/*`，访问封装见 `services/api/src/repositories/*`。


## 开发与质量

- 依赖安装：
  - 基础：`make install`（或 `pip install -r requirements/base.txt && pip install -e packages/common`）
  - 全量：`make install-all`（含 AI/worker/dev 依赖）
- 常用命令（见 `Makefile`）：
  - Lint：`make lint`（ruff + black --check）
  - 格式化：`make format`（black）
  - 测试：`make test`（pytest）
  - 本地栈：`make dev`（Docker compose up）
  - 种子数据：`make seed`（创建默认数据）
- 测试样例：
  - `tests/unit/test_orchestrator.py`：验证 LLM 调度回退逻辑
  - `tests/unit/test_learning_plan.py`：学习计划生成可序列化且字段正确
- 代码风格与工具：
  - Black/Ruff（line-length=100，参见 `pyproject.toml`）
  - 类型检查：mypy（忽略缺失导入）


## CI/CD

GitHub Actions 工作流见 `.github/workflows/ci.yml`：

- 起 Postgres 16 容器，设置 `DATABASE_URL`。
- 安装 `requirements/base.txt`、`requirements/dev.txt` 及可编辑包 `packages/common`。
- 运行质量检查（ruff、black --check）与测试（`pytest -m "not e2e"`）。


## 生产化建议（摘）

- 使用 Alembic 管理数据库迁移（`infra/migrations/` 已预留目录）。
- 接入集中日志与观测（结构化日志、OpenTelemetry）。
- 加强 AI 评测与回归（结构化输出、Rubric、基线）。
- 完善前端（Next.js Web / Admin），通过 `API_BASE_URL` 对接。


## 许可与声明

- 本仓库为专有项目（`pyproject.toml` 中 `license = Proprietary`）。
- `.env.example` 中默认 `DEFAULT_LLM_PROVIDER=mock`，便于无 Key 场景运行；如要接入 DeepSeek/OpenAI，请配置相应 API Key。


---

文件参考（便于快速定位）：

- 后端入口：`services/api/src/main.py:1`
- 路由注册：`services/api/src/api/v1/__init__.py:1`
- 配置中心：`packages/common/src/ai_edu_core/config.py:1`
- 调度器：`services/ai/src/orchestrator.py:1`
- Celery：`services/worker/src/celery_app.py:1`
- Compose：`infra/docker/docker-compose.dev.yml:1`
- 快启脚本：`scripts/dev_quickstart.sh:1`
- CI 工作流：`.github/workflows/ci.yml:1`
