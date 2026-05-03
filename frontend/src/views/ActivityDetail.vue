<template>
  <div class="activity-detail" v-loading="loading">
    <div v-if="activity" class="content">
      <el-page-header @back="$router.back()" :title="activity.activity_name" />
      
      <el-card style="margin-top: 20px">
        <template #header>
          <div class="card-header">
            <h3>{{ activity.activity_name }}</h3>
            <el-tag :type="statusType(activity.status)">{{ statusText(activity.status) }}</el-tag>
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
          </el-descriptions-item>
          <el-descriptions-item label="浏览次数" :span="2">
            {{ activity.view_count }}
          </el-descriptions-item>
          <el-descriptions-item label="活动简介" :span="2">
            {{ activity.description || '无' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 子活动列表 -->
        <div style="margin-top: 30px">
          <h4>子活动</h4>
          <el-table :data="subActivities" style="margin-top: 10px">
            <el-table-column prop="sub_name" label="名称" />
            <el-table-column prop="start_time" label="时间" width="180">
              <template #default="{ row }">{{ formatTime(row.start_time) }}</template>
            </el-table-column>
            <el-table-column prop="location" label="地点" />
          </el-table>
        </div>

        <!-- 标签列表 -->
        <div style="margin-top: 20px">
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
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { activityAPI, subActivityAPI, tagAPI } from '@/api'

const route = useRoute()
const activity = ref(null)
const subActivities = ref([])
const tags = ref([])
const loading = ref(true)

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

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.activity-detail {
  background: white;
  padding: 30px;
  border-radius: 20px;
  min-height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
}
</style>
