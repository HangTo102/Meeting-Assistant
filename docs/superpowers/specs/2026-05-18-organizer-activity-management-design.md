# 主办方活动管理面板 — 设计文档

> 日期：2026-05-18  
> 状态：设计完成，待实施

---

## 1. 概述

当前「主办方上传」tab 登录后只有活动创建表单。需要增加**活动列表管理**功能，让主办方能查看、编辑、删除自己的活动。

---

## 2. 后端改动

### 2.1 新增接口：`GET /api/activities/my`

返回当前登录主办方自己创建的所有活动（不含已取消）。

```
GET /api/activities/my?page=1&page_size=20

Response: [ActivityResponse]
```

**权限**：必须登录  
**排序**：按 `start_time` 降序  
**过滤**：排除 `status = 3`（已取消）

**实现位置**：`app/api/activities.py`，新增路由函数，沿用已有的 `ActivityResponse` schema 和 `get_current_user` 依赖。

---

## 3. 前端改动

### 3.1 API 层（`frontend/src/api/index.js`）

新增：

```js
export const activityAPI = {
  // ...现有方法...
  listMy: (params) => api.get('/activities/my', { params }),  // 新增
}
```

### 3.2 页面层（`frontend/src/views/MainApp.vue`）

#### 3.2.1 布局切换逻辑

登录后不再直接显示上传表单，改为显示活动管理面板。通过一个 `currentView` 状态控制：

| `currentView` 值 | 显示内容 |
|---|---|
| `'list'`（默认） | 活动列表 + 操作按钮 |
| `'create'` | 新建活动表单 |
| `'edit'` | 编辑弹窗（复用创建表单） |

#### 3.2.2 活动列表（`currentView = 'list'`）

```
┌─────────────────────────────────────────────────┐
│  📋 我的活动                     [+ 新建活动]    │
│                                                 │
│  名称          │ 时间范围       │ 状态  │ 操作   │
│  ─────────────┼───────────────┼──────┼─────── │
│  国际创新博览会 │ 03/20 - 03/22 │ 已发布│ ✏️🗑️👁 │
│  音乐节        │ 04/01 - 04/03 │ 草稿  │ ✏️🗑️👁 │
│                                                 │
└─────────────────────────────────────────────────┘
```

- 使用 `el-table` 渲染
- 空状态：显示「暂无活动，点击"新建活动"开始创建」
- 状态列可点击切换（已发布 ↔ 下架），弹窗确认
- 每行操作：编辑、删除、查看详情

#### 3.2.3 新建活动（`currentView = 'create'`）

- 复用现有的上传表单（`<el-form>` 区域）
- 顶部加「← 返回列表」按钮
- 提交成功后自动切回 `'list'` 并刷新

#### 3.2.4 编辑弹窗（`currentView = 'edit'`）

- 使用 `el-dialog` 包裹上传表单
- 打开时预填当前活动的所有字段（activity_name、时间、地址、描述、票务等）
- 子活动区域预填已有子活动数据
- 提交调用 `PUT /activities/{id}`
- 成功后关闭弹窗并刷新列表

#### 3.2.5 删除

- 点击删除 → `ElMessageBox.confirm('确定删除该活动？')`
- 确认后调用 `DELETE /activities/{id}`
- 成功后从列表移除该行，提示「已删除」

#### 3.2.6 查看详情

- 点击 👁 → `el-dialog` 弹出只读详情
- 展示：活动名称、时间、地址、描述、主办方信息、子活动列表、标签、票务信息、浏览数

---

## 4. 数据流

```
用户登录 → GET /api/activities/my → 渲染列表
  │
  ├─ 点击「新建」→ currentView = 'create' → 填写表单 → POST /api/activities
  │                                                      → 刷新列表
  ├─ 点击「编辑」→ currentView = 'edit' → 预填数据 → PUT /api/activities/{id}
  │                                                      → 刷新列表
  ├─ 点击「删除」→ 确认弹窗 → DELETE /api/activities/{id}
  │                          → 刷新列表
  ├─ 点击「详情」→ el-dialog 弹窗只读展示
  └─ 点击状态标签 → PUT /api/activities/{id} (status toggle)
```

---

## 5. 状态管理

新增响应式变量（均在 `MainApp.vue` 的 `<script setup>` 中）：

| 变量 | 类型 | 用途 |
|------|------|------|
| `myActivities` | `ref([])` | 我的活动列表数据 |
| `currentView` | `ref('list')` | 当前视图（list / create / edit） |
| `editingActivity` | `ref(null)` | 正在编辑的活动对象 |
| `detailActivity` | `ref(null)` | 正在查看详情的活动对象 |
| `listLoading` | `ref(false)` | 列表加载状态 |
| `showEditDialog` | `ref(false)` | 编辑弹窗开关 |
| `showDetailDialog` | `ref(false)` | 详情弹窗开关 |

---

## 6. 错误处理

- 列表加载失败 → `ElMessage.error('加载失败')`，保留空列表
- 编辑提交失败 → 弹窗不关闭，`ElMessage.error(response.data.detail)`
- 删除失败 → `ElMessage.error('删除失败')`
- 状态切换失败 → `ElMessage.error('操作失败')`，回滚状态显示

---

## 7. 不改动的部分

- 登录/注册表单：保持不变
- 未登录状态：保持现有的登录框
- 「用户查询」「地图导航」tab：完全不受影响
- 后端已有 CRUD 接口：不修改（仅新增 `/my` 接口）
