# 聊天历史记录 — 设计文档

> 日期：2026-05-18  
> 状态：设计完成，待实施

---

## 1. 概述

当前匿名用户（以及登录主办方）在使用 AI 对话时，`chat_logs` 表中已保存对话记录，但前端未提供查看历史的功能。`session_id` 存在内存中，刷新页面即丢失。

需求：在侧边栏展示历史会话列表，支持点击加载任意历史对话。

---

## 2. 核心设计

### 2.1 会话元信息存储

会话的 ID、标题、时间存放在 **localStorage**，无需后端新增接口。仅点击加载时才调 API 获取完整消息。

```json
{
  "chat_sessions": [
    { "id": "uuid-1", "title": "国际创新博览会在哪里？", "time": "2026-05-17 14:30" },
    { "id": "uuid-2", "title": "音乐节票价多少？", "time": "2026-05-18 09:15" }
  ],
  "active_session": "uuid-2"
}
```

**规则**：
- 最多保留 50 条，超出删最旧的
- 标题取该会话 > 第一条用户消息，截断到 20 个字符
- 时间取第一条消息的发送时间
- 每次新对话发起时，自动追加一条记录
- 已有会话中发送新消息时，更新时间戳并移到列表首位

### 2.2 数据流

```
发送消息 → 有 chatSessionId? 
  ├─ 是 → 更新 localStorage 对应会话的时间
  └─ 否 → 后端返回 session_id → 追加到 localStorage

点击历史会话 → GET /api/chat/history/{session_id}
  → 加载 messages
  → 设置 chatSessionId = session_id
  → 更新 active_session

刷新页面 → 从 localStorage 恢复 active_session
  → 如果存在 → GET /api/chat/history/{session_id} → 恢复消息
  → 如果不存在 → 显示欢迎语
```

---

## 3. UI 布局

### 3.1 侧边栏改动

在三个功能导航按钮**上方**插入历史会话列表区域：

```
┌──────────────────┐
│  🎫 活动助手      │
├──────────────────┤
│  ┌ 历史对话 ────┐ │
│  │ 05-17 14:30  │ │
│  │ 国际创新博览… │ │  ← 活跃会话高亮
│  │              │ │
│  │ 05-16 10:00  │ │
│  │ 最近有什么活… │ │
│  │              │ │
│  │ 05-15 08:20  │ │
│  │ 怎么去会场…  │ │
│  └──────────────┘ │
│                  │
│  💬 用户查询      │
│  📤 主办方上传    │
│  🗺️ 地图导航     │
├──────────────────┤
│  👤 访客用户      │
└──────────────────┘
```

**交互**：
- 历史区域内容超过时，内部独立滚动
- 活跃会话旁有一个小圆点或高亮背景色
- 点击已有会话 → 加载历史消息，当前会话标记为活跃
- 活跃会话始终在列表首位

### 3.2 空状态

- 无历史记录时：历史区域折叠或显示「暂无对话记录」
- 首次使用：不占用空间

---

## 4. 前端改动

### 4.1 `MainApp.vue` — 状态管理

新增变量：

| 变量 | 类型 | 用途 |
|------|------|------|
| `chatSessions` | `ref([])` | localStorage 中的会话元信息列表 |
| `activeSessionId` | `ref(null)` | 当前活跃的 session_id |
| `loadingHistory` | `ref(false)` | 加载历史时的 loading 状态 |

### 4.2 `MainApp.vue` — 方法

新增方法：

| 方法 | 用途 |
|------|------|
| `loadSessionsFromStorage()` | 从 localStorage 读取会话列表 |
| `saveSessionsToStorage()` | 写入 localStorage（含 50 条上限逻辑） |
| `addSessionToHistory(id, title, time)` | 追加/更新一条会话记录 |
| `switchToSession(sessionId)` | 切换到历史会话，调 API 加载消息 |
| `startNewChat()` | 开始新对话，重置 active_session |

### 4.3 无需后端改动

复用已有接口 `GET /api/chat/history/{session_id}`。

---

## 5. 边界情况

| 场景 | 处理 |
|------|------|
| 首次使用，无历史 | 历史区域空白，不占高度 |
| localStorage 已满 | 保留最近 50 条 |
| API 返回空（session 不存在） | ElMessage.warning('该对话记录已过期') |
| API 加载失败 | ElMessage.error('加载失败')，不切换 session |
| 在两个标签页同时聊天 | 各自独立，刷新后以最后一次活跃的为准 |
| 用户手动清除浏览器数据 | localStorage 清空，从零开始 |

---

## 6. 兼容性

- 依赖 `localStorage` API（所有现代浏览器均支持）
- 不依赖 IndexedDB 或 Cookie
- 与主办方注册/管理功能完全解耦，独立实现
