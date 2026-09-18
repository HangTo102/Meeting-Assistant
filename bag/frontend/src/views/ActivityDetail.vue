<template>
  <div class="activity-detail" v-loading="loading">
    <div v-if="activity" class="content">
      <el-page-header @back="$router.back()" :title="activity.activity_name" />

      <el-card style="margin-top: 20px">
        <template #header>
          <div class="card-header">
            <h3>{{ activity.activity_name }}</h3>
            <div class="header-actions">
              <el-tag :type="statusType(activity.status)">{{ statusText(activity.status) }}</el-tag>
              <template v-if="isAdminMode">
                <el-button size="small" type="primary" @click="editActivity">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteActivity">删除</el-button>
              </template>
            </div>
          </div>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="开始时间">
            {{ formatTime(activity.start_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ formatTime(activity.end_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="活动地点" :span="2">
            {{ activity.address }}
          </el-descriptions-item>
          <el-descriptions-item label="票务信息" :span="2">
            {{ activity.requires_ticket ? '需要购票' : '免费入场' }}
            <span v-if="activity.ticket_price"> - {{ activity.ticket_price }}</span>
            <a v-if="activity.ticket_url" :href="activity.ticket_url" target="_blank" class="ticket-link">去购票</a>
          </el-descriptions-item>
          <el-descriptions-item label="浏览次数" :span="2">
            {{ activity.view_count }}
          </el-descriptions-item>
          <el-descriptions-item label="活动简介" :span="2">
            {{ activity.description || '无' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 子活动列表 -->
        <div class="section" v-if="subActivities.length > 0">
          <h4>子活动 / 分会场</h4>
          <el-table :data="subActivities" style="margin-top: 10px">
            <el-table-column prop="sub_name" label="名称" />
            <el-table-column prop="start_time" label="时间" width="180">
              <template #default="{ row }">{{ formatTime(row.start_time) }}</template>
            </el-table-column>
            <el-table-column prop="location" label="地点" />
          </el-table>
        </div>

        <!-- 标签列表 -->
        <div class="section" v-if="tags.length > 0">
          <h4>标签</h4>
          <div style="margin-top: 10px">
            <el-tag v-for="tag in tags" :key="tag.id" style="margin-right: 10px">{{ tag.tag_name }}</el-tag>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { activityAPI, subActivityAPI, tagAPI } from '@/api'

const route = useRoute()
const router = useRouter()

const activity = ref(null)
const subActivities = ref([])
const tags = ref([])
const loading = ref(true)

const isAdminMode = computed(() => route.path.startsWith('/admin'))

const statusType = (status) => {
  const types = { 0: 'info', 1: 'success', 2: 'warning', 3: 'danger' }
  return types[status] || 'info'
}

const statusText = (status) => {
  const texts = { 0: '草稿', 1: '已发布', 2: '已结束', 3: '已取消' }
  return texts[status] || '未知'
}

const formatTime = (time) => {
  if (!time) return '未设置'
  return new Date(time).toLocaleString('zh-CN')
}

const loadData = async () => {
  loading.value = true
  try {
    const [activityRes, subRes, tagRes] = await Promise.all([
      activityAPI.get(route.params.id),
      subActivityAPI.list(route.params.id),
      tagAPI.list(route.params.id),
    ])
    activity.value = activityRes.data
    subActivities.value = subRes.data
    tags.value = tagRes.data
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const editActivity = () => router.push(`/admin/activities/${route.params.id}/edit`)
const deleteActivity = async () => {
  try {
    await ElMessageBox.confirm('确定删除该活动？', '提示', { type: 'warning' })
    await activityAPI.delete(route.params.id)
    ElMessage.success('删除成功')
    router.push('/admin/activities')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.activity-detail {
  background: white;
  padding: 24px;
  border-radius: 16px;
  min-height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.card-header h3 {
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.section {
  margin-top: 30px;
}

.ticket-link {
  margin-left: 12px;
  color: #667eea;
}

@media (max-width: 768px) {
  .activity-detail {
    padding: 16px;
    border-radius: 0;
  }
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
