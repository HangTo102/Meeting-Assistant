<template>
  <div class="activity-list">
    <div class="header">
      <h2>活动列表</h2>
      <el-input v-model="searchQuery" placeholder="搜索活动名称、地点..." prefix-icon="Search" clearable @change="handleSearch" style="width: 300px; margin-right: 15px" />
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button v-if="userStore.token" type="success" @click="$router.push('/admin/activities/create')" style="margin-left: 20px">
        <el-icon><Plus /></el-icon>创建活动
      </el-button>
    </div>

    <el-table :data="activities" v-loading="loading" style="width: 100%">
      <el-table-column prop="activity_name" label="活动名称" min-width="200" />
      <el-table-column prop="start_time" label="开始时间" width="180" />
      <el-table-column prop="end_time" label="结束时间" width="180" />
      <el-table-column prop="address" label="地点" min-width="200" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }"><el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="view_count" label="浏览" width="80" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="viewDetail(row.id)">详情</el-button>
          <el-button v-if="isOwner(row)" link type="primary" @click="editActivity(row.id)">编辑</el-button>
          <el-button v-if="isOwner(row)" link type="danger" @click="deleteActivity(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadActivities" style="margin-top: 20px; justify-content: flex-end" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { activityAPI } from '@/api'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const activities = ref([])
const loading = ref(false)
const searchQuery = ref('')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const ownerId = ref(null)

onMounted(async () => {
  if (userStore.token) {
    try {
      const res = await activityAPI.getCurrentUser()
      ownerId.value = res.data.id
    } catch (e) {}
  }
  loadActivities()
})

const isOwner = (row) => ownerId.value && row.organizer_id === ownerId.value
const statusType = (status) => ({ 0: 'info', 1: 'success', 2: 'warning', 3: 'danger' })[status] || 'info'
const statusText = (status) => { const texts = { 0: '草稿', 1: '已发布', 2: '已结束', 3: '已取消' }; return texts[status] || '未知' }

const loadActivities = async () => {
  loading.value = true
  try {
    const res = await activityAPI.list({ page: page.value, page_size: pageSize.value, status: statusFilter.value || undefined })
    activities.value = res.data
    total.value = res.data.length
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { page.value = 1; searchQuery.value ? activityAPI.search(searchQuery.value).then(res => { activities.value = res.data; total.value = res.data.length }).catch(() => loadActivities()) : loadActivities() }
const viewDetail = (id) => router.push(`/activities/${id}`)
const editActivity = (id) => router.push(`/admin/activities/create?id=${id}`)
const deleteActivity = async (id) => { try { await ElMessageBox.confirm('确定删除?', '提示', { type: 'warning' }); await activityAPI.delete(id); ElMessage.success('删除成功'); loadActivities() } catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') } }
</script>

<style scoped>.activity-list { background: white; padding: 30px; border-radius: 20px; } .header { display: flex; align-items: center; margin-bottom: 20px; gap: 10px; } .header h2 { font-size: 24px; margin-right: 20px; flex-shrink: 0; }</style>
