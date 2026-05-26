# 会场精灵 v2 — 代码质量审计报告

> **审计日期**: 2026-05-18
> **审计范围**: 全项目（前端 Vue 3 + 后端 FastAPI）
> **项目类型**: Python + JavaScript 全栈应用

---

## 1. 项目概况

| 项目 | 内容 |
|------|------|
| **技术栈（前端）** | Vue 3 + Vite + Element Plus + Pinia + Axios |
| **技术栈（后端）** | FastAPI + SQLAlchemy + MySQL + Pydantic |
| **AI 服务** | 通义千问 DashScope |
| **地图服务** | 高德地图 JS API v2.0 |
| **Lint 工具** | ❌ 无 ESLint / 无 ruff / 无 mypy |
| **测试框架** | ❌ 无 |

---

## 2. 总体评分

| 维度 | 评分 | 结果 |
|------|------|------|
| Security（安全） | 3/10 | 🔴 FAIL |
| Code Quality（代码质量） | 4/10 | 🟠 WARNING |
| Architecture（架构） | 4/10 | 🟠 WARNING |
| Functionality（功能） | 5/10 | 🟡 PASS |
| **Overall** | **4/10** | **🟠 WARNING** |

---

## 3. 🔴 Critical — 必须修复

### C1. XSS — `v-html` 未净化

- **位置**: [MainApp.vue:83](file:///e:/program_code/会场精灵v2/frontend/src/views/MainApp.vue#L83), [Chat.vue:24](file:///e:/program_code/会场精灵v2/frontend/src/views/Chat.vue#L24)
- **严重性**: 🔴 严重
- **描述**: AI 返回的 `msg.content` 直接通过 `v-html` 渲染，未经任何 HTML 消毒。如果 AI 返回包含 `<script>` 或恶意标签，就会被浏览器直接执行。这是整个项目最严重的安全隐患。
- **修复建议**: 使用 `v-text` 代替 `v-html`，或引入 [DOMPurify](https://github.com/cure53/DOMPurify) 对 HTML 进行消毒后再渲染。

### C2. CORS 全开

- **位置**: [main.py:30](file:///e:/program_code/会场精灵v2/app/main.py#L30)
- **严重性**: 🔴 严重
- **描述**: `allow_origins=["*"]` 允许任何域名跨域调用 API。生产环境必须限制为实际部署域名。
- **修复建议**: 将 `["*"]` 替换为实际的前端部署域名列表。

### C3. 会话状态内存泄漏

- **位置**: [ai_service.py:14](file:///e:/program_code/会场精灵v2/app/services/ai_service.py#L14)
- **严重性**: 🔴 严重
- **描述**: `SESSION_CONTEXT = {}` 是纯内存字典，永久不清除（`clear_session` 函数存在但从未被调用）。长时间运行后无限膨胀，最终导致 OOM 崩溃。
- **修复建议**: 添加 TTL 过期清理机制（如每 30 分钟清理超过 1 小时未活动的 session）。

---

## 4. 🟠 High — 强烈建议修复

### H1. 路由注册缺失（已修复）

- **位置**: [main.py](file:///e:/program_code/会场精灵v2/app/main.py)
- **描述**: 5 个 API 路由（`navigation`、`chat`、`tags`、`sub_activities`、`upload`）未在 `app.include_router()` 中注册，导致对应接口返回 404。
- **状态**: ✅ **已在本次审计中修复**

### H2. 高德地图认证失败（已修复）

- **位置**: [main.js:12](file:///e:/program_code/会场精灵v2/frontend/src/main.js#L12)
- **描述**: 空 `securityJsCode: ''` 导致高德 JS API 认证失败，地图 SDK 加载后静默报错。同时前端缺少 `VITE_AMAP_KEY` 环境变量时无降级提示。
- **状态**: ✅ **已在本次审计中修复**

### H3. JWT 使用已弃用的 `datetime.utcnow()`

- **位置**: [security.py:30](file:///e:/program_code/会场精灵v2/app/core/security.py#L30)
- **描述**: `datetime.utcnow()` 在 Python 3.12+ 中已弃用，建议改为 `datetime.now(timezone.utc)`。
- **修复建议**: `from datetime import timezone` + `datetime.now(timezone.utc).replace(tzinfo=None)`

### H4. MainApp.vue 巨型组件（1500+ 行）

- **位置**: [MainApp.vue](file:///e:/program_code/会场精灵v2/frontend/src/views/MainApp.vue)
- **描述**: 一个 SFC 包含登录、注册、AI对话、活动上传、地图导航 5 个独立页面功能。严重违反单一职责原则，难以维护和调试。
- **修复建议**: 拆分为独立组件：
  - `ChatPanel.vue`
  - `LoginRegister.vue`
  - `ActivityUpload.vue`
  - `NavigationMap.vue`

### H5. `v-show` vs `v-if` 地图容器

- **位置**: [MainApp.vue:353](file:///e:/program_code/会场精灵v2/frontend/src/views/MainApp.vue#L353)
- **描述**: `amap-container` 用 `v-show` 控制显隐，这是正确的——`v-if` 会销毁 DOM 导致地图实例丢失。
- **状态**: ✅ **无问题**

### H6. 注册后自动登录 — 密码直接传递

- **位置**: [MainApp.vue:598](file:///e:/program_code/会场精灵v2/frontend/src/views/MainApp.vue#L598)
- **描述**: `loginForm.password = registerForm.password` 注册成功后自动登录，密码在前端 JS 对象间传递，违反最小暴露原则。
- **修复建议**: 注册成功后直接调用登录 API，不应复用密码对象。

### H7. Chat API 无认证

- **位置**: [chat.py:38](file:///e:/program_code/会场精灵v2/app/api/chat.py#L38)
- **描述**: `/chat` 接口完全无认证，任何人可无限调用，消耗 AI API 额度和服务器资源。
- **修复建议**: 添加频率限制（rate limit）或可选的 token 认证。

---

## 5. 🟡 Medium — 建议优化

| # | 问题 | 位置 | 说明 | 建议 |
|---|------|------|------|------|
| M1 | Token 存 localStorage | [stores/user.js:10](file:///e:/program_code/会场精灵v2/frontend/src/stores/user.js#L10) | localStorage 可被 XSS 攻击窃取 | 结合 httpOnly Cookie 使用，或确保 C1 修复后风险可控 |
| M2 | 数据库 import 路径混乱 | [auth.py:8](file:///e:/program_code/会场精灵v2/app/api/auth.py#L8) vs [dependencies.py:9](file:///e:/program_code/会场精灵v2/app/core/dependencies.py#L9) | `database.config` vs `app.database.config` 两套路径混用 | 统一为 `app.database.config` |
| M3 | 地图 polyline 解析容错性 | [MainApp.vue:868](file:///e:/program_code/会场精灵v2/frontend/src/views/MainApp.vue#L868) | 坐标解析无空值保护，某个 segment polyline 为空时可能报错 | 添加 `filter(Boolean)` 和 try-catch |
| M4 | 401 vs 403 状态码 | [dependencies.py:11](file:///e:/program_code/会场精灵v2/app/core/dependencies.py#L11) | `HTTPBearer()` 在无 token 时默认返回 403 | 添加自定义异常处理器统一返回 401 |
| M5 | 测试代码含占位密码 | [database/models.py:260](file:///e:/program_code/会场精灵v2/database/models.py#L260) | `__main__` 示例代码中含有 `YOUR_PASSWORD` 等占位符 | 移除或条件编译 `__main__` 代码块 |
| M6 | 无 lint / typecheck 工具 | 项目全局 | 前端无 ESLint，后端无 ruff/mypy，零质量门控 | 添加 ESLint + ruff 配置和 CI 流程 |

---

## 6. 🟢 Low — 可改进项

| # | 问题 | 位置 | 说明 |
|---|------|------|------|
| L1 | 上传目录被 git 跟踪 | [static/uploads/.gitkeep](file:///e:/program_code/会场精灵v2/static/uploads/.gitkeep) | 用户上传的文件可能意外提交 |
| L2 | 内联 style 与 scoped CSS 混用 | [MainApp.vue](file:///e:/program_code/会场精灵v2/frontend/src/views/MainApp.vue) | 大量 `style="margin-bottom: 10px"` 不便统一管理 |
| L3 | 硬编码城市列表 | [retriever.py](file:///e:/program_code/会场精灵v2/app/services/retriever.py) | 仅 8 个城市，无法覆盖全国活动 |
| L4 | 导航硬编码城市为上海 | [navigation.py:37](file:///e:/program_code/会场精灵v2/app/api/navigation.py#L37) | 公交路线规划 `params["city"] = "上海"`，其他城市无法使用公交导航 |

---

## 7. 🏗️ 架构与 SOLID 分析

### SRP — 单一职责原则: ❌ 严重违反

- MainApp.vue 1500+ 行，承载 5 个页面功能
- `database/models.py` 同时包含 ORM 模型 + 数据库管理器 + 测试代码

### OCP — 开闭原则: ⚠️ 部分违反

- `SEMANTIC_MAP` 硬编码在 `retriever.py`，添加新语义类别需修改源码
- 城市列表直接硬编码在检索逻辑中

### DIP — 依赖倒置原则: ⚠️ 部分违反

- `ai_service.py` 直接依赖 `dashscope.Generation`，没有抽象层
- 更换 AI 供应商需大幅修改代码

### DRY — 不重复原则: ⚠️ 部分违反

- 登录/注册逻辑在 `Login.vue` 和 `MainApp.vue` 中各实现一套，几乎完全重复
- `get_db` 在 `database/config.py` 和 `app/core/dependencies.py` 中各定义一次

---

## 8. 基于审计的安全加固建议

### 推荐修复开发流程

```
开发 → 提交前(手动审查) → PR(人工Code Review) → 部署
                              ↓
                     缺少自动化检查
```

### 建议添加的工具链

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| ESLint | 前端代码规范 | `npm install -D eslint` |
| ruff | Python 代码规范 + 自动修复 | `pip install ruff` |
| mypy | Python 类型检查 | `pip install mypy` |

---

## 9. 优先级修复清单

```
Priority 1 (立即修复)
  ├── C1: XSS v-html 净化
  ├── C2: CORS 限制域名
  └── C3: 会话内存泄漏

Priority 2 (本周内)
  ├── H4: 拆分 MainApp.vue
  ├── H7: Chat API 添加频率限制
  └── M2: 统一 import 路径

Priority 3 (本月内)
  ├── H3: 修复 utcnow 弃用
  ├── M6: 添加 lint 工具
  └── L4: 导航城市动态化
```

---

## 10. 本次已完成的修复

| 修复 | 涉及文件 | 说明 |
|------|----------|------|
| ✅ 高德地图认证 | [main.js](file:///e:/program_code/会场精灵v2/frontend/src/main.js) | 移除空 securityJsCode，支持域名白名单方式 |
| ✅ initMap 时序优化 | [MainApp.vue:775](file:///e:/program_code/会场精灵v2/frontend/src/views/MainApp.vue#L775) | 增加 `__amapReady` 标记检测防遗漏，防重复初始化 |
| ✅ 地图容器高度修复 | [MainApp.vue:1480](file:///e:/program_code/会场精灵v2/frontend/src/views/MainApp.vue#L1480) | 添加 `min-height: 400px` 防止高度塌陷 |
| ✅ 注册缺失路由 | [main.py](file:///e:/program_code/会场精灵v2/app/main.py) | 注册 navigation/chat/sub_activities/tags/upload 路由 |

---

> **审计工具**: Code Quality Audit Skill
> **审计方式**: 手动代码审查（项目无自动化工具）
