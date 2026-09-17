<template>
  <div class="activity-list">
    <div class="header">
      <h2>{{ pageTitle }}</h2>
      <div class="header-actions">
        <el-input
          v-model="searchQuery"
          placeholder="搜索活动名称、地点..."
          prefix-icon="Search"
          clearable
          @change="handleSearch"
          style="width: 220px"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button
          v-if="isAdminMode"
          type="success"
          @click="$router.push('/admin/activities/create')"
        >
          <el-icon><Plus /></el-icon>创建活动
        </el-button>
      </div>
    </div>

    <el-tabs v-if="!isAdminMode" v-model="statusTab" @tab-change="loadActivities" class="status-tabs">
      <el-tab-pane label="全部" name="all" />
      <el-tab-pane label="即将开始" name="upcoming" />
      <el-tab-pane label="进行中" name="ongoing" />
      <el-tab-pane label="已结束" name="ended" />
    </el-tabs>

    <!-- 桌面端表格 -->
    <el-table
      v-if="!isMobile"
      :data="displayActivities"
      v-loading="loading"
      style="width: 100%"
    >
      <el-table-column prop="activity_name" label="活动名称" min-width="180" />
      <el-table-column label="时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.start_time) }} ~ {{ formatDate(row.end_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="address" label="地点" min-width="180" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="!isAdminMode" prop="view_count" label="浏览" width="80" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="viewDetail(row.id)">详情</el-button>
          <template v-if="isAdminMode">
            <el-button link type="primary" @click="editActivity(row.id)">编辑</el-button>
            <el-button link type="danger" @click="deleteActivity(row.id)">删除</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <!-- 移动端卡片 -->
    <div v-else class="mobile-cards">
      <div v-for="act in displayActivities" :key="act.id" class="activity-card">
        <div class="card-title">{{ act.activity_name }}</div>
        <div class="card-meta">
          <span>{{ formatDate(act.start_time) }}</span>
          <el-tag :type="statusType(act.status)" size="small">{{ statusText(act.status) }}</el-tag>
        </div>
        <div class="card-address">{{ act.address }}</div>
        <div class="card-actions">
          <el-button size="small" @click="viewDetail(act.id)">详情</el-button>
          <template v-if="isAdminMode">
            <el-button size="small" type="primary" @click="editActivity(act.id)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteActivity(act.id)">删除</el-button>
          </template>
        </div>
      </div>
    </div>

    <el-pagination
      v-if="!isAdminMode"
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :total="total"
      layout="total, prev, pager, next"
      @current-change="loadActivities"
      style="margin-top: 20px; justify-content: flex-end"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { activityAPI } from '@/api'
import { Plus } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isAdminMode = computed(() => route.path.startsWith('/admin'))
const pageTitle = computed(() => isAdminMode.value ? '我的活动' : '活动列表')

const activities = ref([])
const loading = ref(false)
const searchQuery = ref('')
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)
const statusTab = ref('all')

const displayActivities = computed(() => {
  if (isAdminMode.value) return activities.value
  if (statusTab.value === 'all') return activities.value
  const now = new Date()
  return activities.value.filter(act => {
    const start = new Date(act.start_time)
    const end = new Date(act.end_time)
    if (statusTab.value === 'upcoming') return start > now
    if (statusTab.value === 'ongoing') return start <= now && end >= now
    if (statusTab.value === 'ended') return end < now
    return true
  })
})

const isMobile = ref(window.innerWidth < 768)
const onResize = () => { isMobile.value = window.innerWidth < 768 }

onMounted(() => {
  window.addEventListener('resize', onResize)
  loadActivities()
})
onUnmounted(() => window.removeEventListener('resize', onResize))

const statusType = (status) => ({ 0: 'info', 1: 'success', 2: 'warning', 3: 'danger' })[status] || 'info'
const statusText = (status) => {
  const texts = { 0: '草稿', 1: '已发布', 2: '已结束', 3: '已取消' }
  return texts[status] || '未知'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const loadActivities = async () => {
  loading.value = true
  try {
    let res
    if (isAdminMode.value) {
      res = await activityAPI.getMyActivities()
      activities.value = res.data
      total.value = res.data.length
    } else {
      const params = { page: page.value, page_size: pageSize.value, status: 1 }
      res = await activityAPI.list(params)
      activities.value = res.data
      total.value = res.data.length
    }
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  if (!searchQuery.value.trim()) {
    loadActivities()
    return
  }
  page.value = 1
  activityAPI.search(searchQuery.value)
    .then(res => {
      activities.value = res.data
      total.value = res.data.length
    })
    .catch(() => loadActivities())
}

const viewDetail = (id) => {
  router.push(isAdminMode.value ? `/admin/activities/${id}` : `/activities/${id}`)
}
const editActivity = (id) => router.push(`/admin/activities/${id}/edit`)
const deleteActivity = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除该活动？', '提示', { type: 'warning' })
    await activityAPI.delete(id)
    ElMessage.success('删除成功')
    loadActivities()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.activity-list {
  background: white;
  padding: 24px;
  border-radius: 16px;
}
.header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 12px;
}
.header h2 {
  font-size: 22px;
  margin: 0;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.status-tabs {
  margin-bottom: 16px;
}
.mobile-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.activity-card {
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 16px;
}
.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}
.card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #666;
  font-size: 13px;
  margin-bottom: 8px;
}
.card-address {
  color: #999;
  font-size: 13px;
  margin-bottom: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card-actions {
  display: flex;
  gap: 8px;
}
@media (max-width: 768px) {
  .activity-list {
    padding: 16px;
    border-radius: 0;
  }
  .header {
    flex-direction: column;
    align-items: flex-start;
  }
  .header-actions {
    width: 100%;
  }
  .header-actions .el-input {
    flex: 1;
  }
}
</style>
