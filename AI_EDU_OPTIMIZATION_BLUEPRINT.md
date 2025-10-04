# AI+教育教学项目 全栈重构与优化蓝图（落地级）

版本：v1.0（初稿）
日期：2025-10-04
范围：覆盖现有所有目录与文件，提供创新能力规划、工程化重构方案、质量与安全合规体系，目标达到可在真实教育教学环境落地运行的工程级水准。

---

## 0. 现状扫描与目录遍历（不遗漏层级）

本节基于完整目录扫描，排除`.git/.venv/node_modules/__pycache__`等环境与缓存后形成的清单。完整扫描文件：`PROJECT_TREE_CLEAN.txt`。以下为当前仓库（精简视图）：

```
./.idea
./.idea/.gitignore
./.idea/inspectionProfiles
./.idea/inspectionProfiles/profiles_settings.xml
./.idea/misc.xml
./.idea/modules.xml
./.idea/vcs.xml
./.idea/workspace.xml
./.idea/人工智能+项目（代码）.iml
./PROJECT_DIRS.txt
./PROJECT_EXT_STATS.txt
./PROJECT_FILES.txt
./PROJECT_LINE_COUNTS.tsv
./PROJECT_SUMMARY.txt
./PROJECT_TREE.txt
./PROJECT_TREE_CLEAN.txt
./README.md
./ai_core.py
./app.py
./assets
./assets/logo.png
./data
./data/community_data.json
./data/knowledge_graph.json
./data/user_.json
./data/user_data.csv
./data/user_default.json
./data/user_清华大学预备生.json
./data/user_罪罪州.json
./pages
./pages/.env.example
./pages/.gitignore
./pages/1_学习社区.py
./pages/2_学习计划.py
./pages/3_知识图谱.py
./pages/4_数据分析.py
./pages/5_成就系统.py
./query
./requirements.txt
./test_mongodb.py
./user_data.py
./智能体图标.png
```

统计（Clean）：
- 文件：见 `PROJECT_SUMMARY_CLEAN.txt`（Files: 37）
- 目录：见 `PROJECT_SUMMARY_CLEAN.txt`（Dirs: 5）
- 扩展名Top10：`txt(10), py(9), json(6), xml(5), md(1)…`

关键代码概览：
- `app.py`：Streamlit 主应用，登录/导航/AI问答/错题本/建议/进度/成就等。
- `ai_core.py`：OCR（PaddleOCR）、学科识别、提示词选择、DeepSeek Chat 调用、基础知识图谱（NetworkX）。
- `user_data.py`：用户数据（混合JSON文件与MongoDB），注册登录（SHA-256无盐）、学习数据统计与成就。
- `pages/*.py`：Streamlit 多页面（学习社区、学习计划、知识图谱、数据分析、成就系统）。
- `data/*.json`：社区与用户示例数据、知识图谱初始文件。
- `requirements.txt`：编码异常（疑似UTF-16/带NUL），依赖声明失效风险。
- `test_mongodb.py`：本地Mongo连通性与CRUD简测。

主要问题清单（需在重构中根治）：
- 架构：前后端与业务/AI耦合在Streamlit，难以扩展与测试；无统一API层；数据读写混杂JSON文件与Mongo，缺乏事务与一致性保障。
- 安全：密码哈希无盐；未使用JWT/OIDC；敏感配置缺少`.env`规范；缺少权限模型与多租户隔离；社区/资源数据可被任意用户删除。
- 数据：用户学习记录、错题、知识图谱均以文件散存，缺少规范化数据模型与索引；无法支撑多用户与课堂级场景。
- AI能力：仅单轮回答；无检索增强（RAG）、无工具调用；无提示工程规范/评测；无法离线/多模型切换；OCR流水线缺少幂等与缓存。
- 质量：几乎无单元/集成测试、类型约束、lint；错误处理散乱；缺少CI/CD、可观测性。
- 合规：未体现隐私合规（未成年人、家长同意、数据保留策略）、审计与内容安全。
- 前端：Streamlit适合原型，不利于大规模课堂/多端访问；无无障碍（WCAG）与i18n建设。
- 依赖：`requirements.txt`编码错误，影响部署；PaddleOCR重量级依赖，需可选化与容器化隔离。

---

## 1. 愿景与目标（创新与落地）

愿景：打造“AI原生”的个性化学习与教学平台，覆盖学生与教师侧真实使用场景，具备可评估的学习增益与课堂落地能力。

落地目标：
- 教学闭环：题目采集→理解→解答→错题归档→复习计划→知识追踪→学习成就。
- 教师助手：作业出题、评分与讲评、班级看板、薄弱点分析、分层教学建议。
- 学习同伴体：结构化步骤提示、类苏格拉底式引导、分阶段提示与反思。
- 规模化能力：多租户（学校/班级/小组）、RBAC、LTI 1.3接入主流LMS（Canvas/Moodle）、xAPI事件上报。
- AI工程化：可插拔模型（DeepSeek/OpenAI/Azure/本地），RAG/工具调用/安全护栏，离线应急。
- 效果评测：DKT/BKT知识追踪，学习增益A/B实验，Rubric对齐的自动评分与一致性评估。

关键KPI：
- 学习增益：前后测提升≥15%；知识点掌握AUC≥0.75。
- 可靠性：P95答复延迟≤3s（纯文本）；≥99.5%可用性。
- 数据安全：0高危漏洞；敏感数据加密覆盖率100%。
- 质量：单元/集成测试覆盖≥70%；关键路径端到端测试稳定通过。

---

## 2. 目标架构（高层设计）

建议“前后端分离 + 可插拔AI编排 + 数据中台”的分层：

应用层：
- Web前端（首期可保留Streamlit作为运营与内管；面向C端建议Next.js/React重构）。
- 教师控制台（班级/作业/评分/看板）。

服务层（FastAPI微服务/模块化单体）：
- API Gateway（GraphQL或REST，统一鉴权/限流/审计）。
- Auth服务（OIDC/JWT，RBAC，多租户/组织/班级/角色：学生/教师/家长/管理员）。
- 用户与档案服务（Profile、家长关联、同意书）。
- 学习与错题服务（题目、解答、错题、复习计划、间隔重复）。
- 知识图谱服务（概念、依赖、掌握度、个性化子图）。
- 推荐服务（自适应学习、题目推荐、资源推荐）。
- AI编排服务（LLM路由、RAG、工具调用、提示模板、结构化输出校验）。
- OCR与文档解析服务（图片/PDF/EPUB，缓存与去重）。
- 社区与资源服务（讨论/问答/资源，审核与内容安全）。
- 分析与可观测性服务（学习数据聚合、指标、日志、追踪）。

数据层：
- 关系型：PostgreSQL（用户、课程、作业、错题、会话、审计）。
- 文档/图：MongoDB（可选）/Neo4j（知识图谱）或以Postgres+pgvector替代。
- 向量库：Qdrant/FAISS/pgvector（内容检索与用户语料索引）。
- 缓存与队列：Redis（限流、会话、任务队列）。
- 对象存储：S3兼容（题图、讲义、音视频）。

基础设施：
- 容器化（Docker）、编排（K8s）、CDN与边缘缓存（静态资源/模型缓存）。
- 可观测性：OpenTelemetry + Prometheus + Grafana + Sentry。

---

## 3. 模块化设计与创新能力

3.1 AI编排与安全护栏
- Provider适配层：OpenAI/DeepSeek/Azure/本地vLLM统一接口；可按租户/学科智能路由。
- RAG：教辅/讲义/课堂资料/错题语料索引，支持增量更新与版本化；重排器提升命中质量。
- 多Agent协作：
  - 题目理解Agent（OCR/主题/难度/知识点定位）。
  - 学科求解Agent（学科特定提示、工具集、可控推理风格）。
  - 教学法Agent（分步提示、支架式提问、错误诊断与再引导）。
  - 评分与Rubric Agent（结构化评分+解释+锚定例）。
  - 审核Agent（内容安全、偏见/敏感性检查）。
- 结构化输出：Pydantic JSON模式校验；异常回退策略与置信度标注。
- 评测：基于rubric的主观题一致性评估，MSE/AUC/Exact Match等客观题指标。

3.2 知识追踪与推荐
- DKT/BKT/IRT并行评估；用户掌握向量与知识图谱节点对齐。
- 间隔重复（SM-2/FSRS）驱动复习计划；“需要巩固”候选集生成。
- 班级/小组维度的薄弱点聚类与差异化分层教学建议。

3.3 教师与课堂能力
- 作业自动出题（难度/知识点/题型控制），一键讲评PPT/讲义生成。
- 自动评分+批注；错因统计图；家校沟通摘要。
- LMS互通：LTI 1.3（SSO、成绩回传），xAPI学习事件上报。

3.4 多模态学习
- 图片/OCR题、手写批注识别、作答纸扫描。
- 语音问答（ASR/TTS）与口语纠错；听力材料精听打点。

---

## 4. 数据模型（核心实体与关系）

建议使用PostgreSQL为主库，关键表与字段示例：
- `tenants(id, name, ... )` 多租户/学校。
- `users(id, tenant_id, role, username, password_hash, parent_id, consent_state, ... )`。
- `classes(id, tenant_id, name, teacher_id, ... )`、`enrollments(user_id, class_id, role)`。
- `problems(id, subject, knowledge_tags[], difficulty, content, media_refs[])`。
- `answers(id, problem_id, user_id, content, score, rubric, model_used, latency_ms, ...)`。
- `mistakes(id, user_id, problem_id, reason, knowledge_tags[], created_at)`。
- `study_sessions(id, user_id, start, end, duration_h, device)`。
- `knowledge_nodes(id, subject, name, description)`、`knowledge_edges(src, dst, relation)`。
- `recommendations(id, user_id, candidate_id, type, reason, created_at)`。
- 审计与内容安全：`audit_events(...)`、`content_moderation(...)`。

向量与检索：
- `embeddings(id, owner_id, type, vector, ref_table, ref_id, version)`（pgvector/Qdrant）。

对象存储规范：
- Key设计：`{tenant}/{class}/{user}/{type}/{date}/{uuid}.{ext}`；所有外链签名+过期。

---

## 5. API 设计（示例）

认证与用户：
- `POST /auth/login`（OIDC或本地）→ JWT（含租户/角色/班级）。
- `POST /users` 注册（强校验+短信/邮箱验证，可选家长同意）。

学习与错题：
- `POST /qa` 提交问题（文本/图片URL）→ `answer_id`、结构化结果（步骤、公式、可视化）。
- `POST /mistakes` 收藏错题（知识点、难度、原因）。
- `GET /plan` 个性化学习计划（间隔重复+知识图谱弱点）。

知识图谱：
- `GET /kg/{subject}` 拉取个性化子图；`POST /kg/nodes` 新增节点；`POST /kg/edges` 建边。

推荐：
- `GET /recommendations` 学习资源与题目推荐，带来源解释与可追溯证据。

社区：
- `GET/POST /community/discussions|questions|resources`，带审核与Owner策略；软删除+审计。

所有写请求均记录`audit_events`并绑定操作者与租户。

---

## 6. AI 能力与工程化

模型与路由：
- 统一`/providers`抽象（DeepSeek/OpenAI/Azure/本地vLLM）；按`subject`/`latency`/`cost`动态路由；失败降级与缓存。

提示与输出：
- Prompt模板化+版本管理；输出用Pydantic校验（JSON模式）；异常时自动重试/温度调节。

RAG：
- 资料分块（语义/版面）、向量化、重排，检索证据信心阈值；提示中显示证据片段与来源。

工具：
- 公式求解/单位换算/绘图（SymPy/NumPy/Plotly）作为安全的工具调用；防注入与沙箱。

评测与监控：
- 题集基准+rubric对齐；一致性、幻觉率、延迟、成本四象限监控；数据可回放。

离线与隐私：
- 本地小模型快速问答/敏感场景；用户选择开关与本地优先策略；模型资产隔离。

---

## 7. 安全、合规与内容治理

身份与权限：
- OIDC/JWT；RBAC（学生/教师/家长/管理员）；多租户隔离（Row-Level Security/租户ID贯穿）。

密码与凭据：
- Argon2/BCrypt加盐哈希；API Key与Secrets使用`.env`+密钥管理（如SOPS/KMS），严禁入库明文。

隐私合规：
- 中国《个保法》/GDPR/FERPA对齐：最小化采集、目的限制、数据保留与删除、家长同意（未成年人）。
- 数据分级：PII加密（静态/传输），访问审计与告警，导出与删除请求通道。

内容安全：
- 题目/讨论/资源发布前后置审核；敏感词/涉政涉暴等检测；AI输出安全护栏与再检查。

---

## 8. 可观测性、质量与效能

质量：
- 类型约束（mypy/pyright）、风格（ruff/black）、安全扫描（bandit）。
- 测试金字塔：单元/集成/契约/端到端（Playwright）。关键链路（登录→提问→收藏→计划）必须覆盖。

可观测性：
- 结构化日志（JSON）、分布式追踪（OpenTelemetry）、业务指标（学习增益/延迟/命中率）。
- 错误追踪（Sentry）；SLO/SLI仪表盘（Grafana）。

CI/CD：
- GitHub Actions：lint+test+docker build+安全扫描；环境分层（dev/staging/prod）。

---

## 9. 前端与体验（可分阶段）

阶段1（保留Streamlit）：
- 将AI与数据访问迁移到后端API；Streamlit仅负责调用API并渲染；统一Session与权限校验。

阶段2（C端重构）：
- Next.js（App Router）+ Tailwind + i18n；移动端适配；组件化答题卡/步骤提示/错题卡；键盘操作与无障碍支持（WCAG 2.1 AA）。

教师端：
- 班级管理、作业布置、自动评分结果审阅、一键讲评、家长摘要；班级对比与干预建议。

---

## 10. 迁移与重构计划（分阶段）

Phase 0：环境与依赖修复（1周）
- 修复`requirements.txt`编码为UTF-8，按平台分组可选依赖（如PaddleOCR）。
- 引入`.env`与配置加载；区分本地/测试/生产；禁用明文密钥。
- 容器化Streamlit与PaddleOCR（可选GPU镜像），提供`docker-compose`本地编排。

Phase 1：后端基线（2-3周）
- 新建`services/api`（FastAPI）：认证、用户、错题、学习会话基础CRUD与审计；迁移`user_data.py`至ORM（SQLModel/SQLAlchemy）。
- Auth：BCrypt/Argon2加密，JWT颁发与续签；RBAC与多租户上下文注入；速率限制。
- 日志/监控/测试基建；数据迁移脚本（JSON→DB）。

Phase 2：AI编排与RAG（2-4周）
- 新建`services/ai`：Provider适配（DeepSeek/OpenAI/Azure/Local）、提示模板、结构化输出、重试与缓存。
- 新建`services/worker`（Celery/RQ+Redis）：OCR/嵌入/批处理。
- 新建`services/retrieval`：索引构建、RAG查询；接入课程资料与错题语料。

Phase 3：教学能力与知识追踪（3-5周）
- DKT/BKT模块；掌握度估计对齐知识图谱；复习与计划生成（SM-2/FSRS）。
- 教师端：作业出题、自动评分与讲评；班级看板与薄弱点分析。

Phase 4：安全合规与对外集成（2-3周）
- 审计、内容安全、数据保留与导出、家长同意流程。
- LTI 1.3对接主流LMS、xAPI事件上报；SAML/OIDC企业接入。

Phase 5：前端重构与优化（2-4周）
- Next.js前端上线；Streamlit保留为内部运营与试验工具。

---

## 11. 目录重构建议（Monorepo示例）

```
.
├─ apps/
│  ├─ web/                 # Next.js 前端（C端）
│  └─ admin/               # 管理/教师端
├─ services/
│  ├─ api/                 # FastAPI（REST/GraphQL），Auth/RBAC/审计
│  ├─ ai/                  # LLM编排、RAG、提示模板、评测
│  ├─ retrieval/           # 索引与向量服务
│  └─ worker/              # Celery/RQ 任务执行（OCR/嵌入）
├─ packages/
│  ├─ common/              # 共享模型/协议/工具
│  └─ clients/             # 各服务SDK（Python/TS）
├─ infra/
│  ├─ docker/              # 镜像与compose
│  ├─ k8s/                 # 部署编排
│  └─ migrations/          # 数据迁移
├─ docs/                   # 设计文档、提示模板、评测基准
└─ tests/                  # 单元/集成/契约/端到端
```

现有`pages/*.py`与`app.py`可在Phase 1保留，通过HTTP调用`services/api`；逐步迁移UI逻辑。

---

## 12. 代码规范与工程质量基线

- Python：3.10+；类型注解全覆盖；`ruff`+`black`+`mypy`；结构化日志（`structlog`）。
- API：Pydantic v2模型；错误以RFC7807问题详情返回；速率限制与重试。
- 测试：pytest（fixtures、fastapi testclient、playwright e2e）；数据工厂与合成数据。
- 安全：依赖扫描（pip-audit）、静态检查（bandit）、密钥扫描（gitleaks）。

---

## 13. 已有问题的修复与迁移要点

- `requirements.txt`编码异常：改为UTF-8纯文本，并按功能分组：
  - 基础：`streamlit>=1.25.0`, `pydantic>=2`, `fastapi`, `uvicorn`, `sqlalchemy`。
  - AI：`openai`/`litellm`, `qdrant-client`/`pgvector`, `numpy`, `scipy`, `sympy`。
  - 可选：`paddleocr`（放入`extras[ocr]`）。
- 密钥管理：移除代码内`base_url`/Key硬编码；改用`ENV`与Provider路由。
- 认证与存储：
  - 密码改为`Argon2/BCrypt`；
  - 用户/错题/交互记录迁移至Postgres；
  - 社区数据由JSON迁移至表并加权限与审计；
  - 知识图谱统一为服务+持久化（关系或图DB）。
- OCR：加入缓存（文件指纹），失败退避与重试；容器化隔离。

---

## 14. 验收与评测

- 功能验收：登录→提问→收藏→计划→复习→成就链路全流程稳定。
- AI效果：
  - 主观题Rubric一致性≥基线；
  - RAG证据命中率、幻觉率可量化并可视化。
- 教学场景：
  - 作业出题/评分/讲评可在班级规模运行；
  - 教师看板数据准确、延迟可接受。
- 安全合规：
  - 渗透与隐私检查通过；
  - 家长同意与数据导出删除流程可用。

---

## 15. 风险与缓解

- 重依赖（OCR/大模型）导致镜像体积与冷启动：采用可选化/分层镜像/预热与缓存。
- 学校内网/无外网：本地小模型、延迟队列与离线包。
- 数据迁移复杂度：编写灰度迁移脚本与双写期；回滚预案。
- 法规与内容安全：与法务/德育协作，保守默认、最小化采集与透明告知。

---

## 16. 里程碑与工作量（粗估）

- P0（1周）：依赖修复、容器化、本地可跑、基础监控。
- P1（2-3周）：API基线与数据迁移、认证与权限、Streamlit对接API。
- P2（2-4周）：AI编排/RAG、任务队列、文档解析。
- P3（3-5周）：知识追踪/教师能力、看板与作业闭环。
- P4（2-3周）：合规与LTI/xAPI对接。
- P5（2-4周）：前端重构与性能调优。

---

## 附录A：完整目录清单与统计

- 目录树（Clean）：见 `PROJECT_TREE_CLEAN.txt`（已包含在仓库根目录）
- 文件清单：`PROJECT_FILES_CLEAN.txt`
- 扩展名统计：`PROJECT_EXT_STATS_CLEAN.txt`
- 行数统计：`PROJECT_LINE_COUNTS_CLEAN.tsv`
- 摘要：`PROJECT_SUMMARY_CLEAN.txt`

（如需将清单内嵌到文档，可直接复制上述文件内容。）

---

## 附录B：迁移映射（旧→新）

- `app.py/pages/*.py` → `services/api`（业务API）与前端（UI）。
- `user_data.py`（JSON/Mongo） → Postgres（ORM模型：Users, Mistakes, Sessions...）。
- `ai_core.py` → `services/ai`（Provider、Prompt、RAG、工具、评测）。
- `data/*.json` → 迁移脚本导入数据库（并落对象存储）。

---

## 附录C：落地建议与示例脚手架

开发脚本（Makefile任务建议）：
- `make dev` 本地启动（api/worker/web）
- `make test` 运行测试
- `make lint` 代码规范检查
- `make seed` 载入示例数据

Docker Compose（示例服务）：
- `api`（FastAPI）、`worker`（Celery+Redis）、`db`（Postgres+pgvector）、`qdrant`（可选）、`minio`（对象存储）、`otel-collector`、`grafana`、`prometheus`、`sentry`（可选）。

---

以上蓝图覆盖现有项目的每一层级目录扫描、现状问题、面向教育教学落地的创新能力与工程化重构路线。后续可按阶段推进开发与迁移，逐步将现有Streamlit原型演进为可在校园/机构真实部署与使用的生产级系统。

