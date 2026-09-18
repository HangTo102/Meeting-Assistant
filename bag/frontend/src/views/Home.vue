<template>
  <div class="home-page">
    <!-- 顶部导航 -->
    <header class="navbar">
      <div class="logo" @click="$router.push('/home')">🎯 会场精灵</div>
      <div class="nav-links" :class="{ open: mobileMenuOpen }">
        <el-button text @click="$router.push('/home')">首页</el-button>
        <el-button text @click="$router.push('/activities')">活动列表</el-button>
        <el-button text @click="$router.push('/app')">AI 助手</el-button>
        <el-button v-if="!userStore.token" type="primary" @click="$router.push('/login')">主办方登录</el-button>
        <el-button v-else type="danger" @click="handleLogout">退出</el-button>
      </div>
      <el-button class="mobile-menu-btn" text @click="mobileMenuOpen = !mobileMenuOpen">
        <el-icon :size="24"><Menu /></el-icon>
      </el-button>
    </header>

    <!-- Hero 区域 -->
    <section class="hero">
      <h1>探索精彩活动</h1>
      <p>汇聚各类精彩活动，AI 智能助手随时为您解答</p>
      <div class="hero-actions">
        <el-button type="primary" size="large" @click="$router.push('/app')">进入会场</el-button>
        <el-button size="large" @click="$router.push('/login')">主办方入口</el-button>
      </div>
    </section>

    <!-- 全部公开活动 -->
    <section class="section">
      <div class="container">
        <h2>📅 全部活动</h2>
        <el-tabs v-model="statusFilter" @tab-change="loadActivities">
          <el-tab-pane label="全部" name="all" />
          <el-tab-pane label="即将开始" name="upcoming" />
          <el-tab-pane label="进行中" name="ongoing" />
          <el-tab-pane label="已结束" name="ended" />
        </el-tabs>

        <el-row :gutter="20">
          <el-col
            v-for="act in filteredActivities"
            :key="act.id"
            :xs="24" :sm="12" :md="8" :lg="6"
            style="margin-bottom: 20px"
          >
            <el-card shadow="hover" class="activity-card" @click="viewDetail(act.id)">
              <h3>{{ act.activity_name }}</h3>
              <p class="time">{{ formatDate(act.start_time) }} - {{ formatDate(act.end_time) }}</p>
              <p class="address">📍 {{ act.address }}</p>
              <div class="tags">
                <el-tag size="small" v-for="tag in (act.tag_list || [])" :key="tag">{{ tag }}</el-tag>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <div v-if="filteredActivities.length === 0" class="empty">暂无活动</div>
      </div>
    </section>

    <!-- 功能特色 -->
    <section class="section features" style="background: white;">
      <div class="container">
        <h2>✨ 功能特色</h2>
        <el-row :gutter="40">
          <el-col :xs="24" :sm="8">
            <div class="feature-item">
              <div class="feature-icon">📅</div>
              <h3>活动查询</h3>
              <p>快速查找各类活动信息</p>
            </div>
          </el-col>
          <el-col :xs="24" :sm="8">
            <div class="feature-item">
              <div class="feature-icon">🤖</div>
              <h3>AI 助手</h3>
              <p>智能客服随时解答问题</p>
            </div>
          </el-col>
          <el-col :xs="24" :sm="8">
            <div class="feature-item">
              <div class="feature-icon">📍</div>
              <h3>精准定位</h3>
              <p>详细地点和交通指南</p>
            </div>
          </el-col>
        </el-row>
      </div>
    </section>

    <!-- 底部 -->
    <footer class="footer">
      <p>© 2026 会场精灵 | 活动信息智能助手</p>
      <p style="font-size: 12px; color: #999;">仅供学习交流使用</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { activityAPI } from '@/api'
import { Menu } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const statusFilter = ref('all')
const activities = ref([])
const mobileMenuOpen = ref(false)

const filteredActivities = computed(() => {
  const now = new Date()
  return activities.value.filter(act => {
    if (statusFilter.value === 'all') return true
    const start = new Date(act.start_time)
    const end = new Date(act.end_time)
    if (statusFilter.value === 'upcoming') return start > now
    if (statusFilter.value === 'ongoing') return start <= now && end >= now
    if (statusFilter.value === 'ended') return end < now
    return true
  })
})

const loadActivities = async () => {
  try {
    const res = await activityAPI.list({ page: 1, page_size: 100, status: 1 })
    activities.value = res.data
  } catch (e) {
    console.error('加载活动失败', e)
  }
}

const viewDetail = (id) => router.push(`/activities/${id}`)

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日 ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const handleLogout = () => {
  userStore.logout()
  location.reload()
}

onMounted(loadActivities)
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: white;
  padding: 15px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  font-size: 24px;
  font-weight: bold;
  color: #667eea;
  cursor: pointer;
}

.nav-links {
  display: flex;
  gap: 10px;
  align-items: center;
}

.mobile-menu-btn {
  display: none;
}

.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 80px 30px;
  text-align: center;
  color: white;
}

.hero h1 {
  font-size: 48px;
  margin-bottom: 20px;
}

.hero p {
  font-size: 18px;
  margin-bottom: 40px;
  opacity: 0.9;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.section {
  padding: 60px 30px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.activity-card {
  height: 100%;
  cursor: pointer;
  transition: transform 0.2s;
}

.activity-card:hover {
  transform: translateY(-4px);
}

.activity-card h3 {
  margin: 0 0 10px;
  font-size: 16px;
}

.activity-card .time {
  color: #666;
  font-size: 14px;
  margin: 5px 0;
}

.activity-card .address {
  color: #999;
  font-size: 14px;
  margin: 5px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.activity-card .tags {
  margin-top: 10px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.empty {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

.feature-item {
  text-align: center;
  padding: 40px 20px;
}

.feature-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.footer {
  background: #333;
  color: white;
  padding: 30px;
  text-align: center;
  margin-top: auto;
}

@media (max-width: 768px) {
  .navbar {
    padding: 12px 16px;
  }

  .nav-links {
    display: none;
    position: absolute;
    top: 60px;
    left: 0;
    right: 0;
    background: white;
    flex-direction: column;
    padding: 16px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  }

  .nav-links.open {
    display: flex;
  }

  .mobile-menu-btn {
    display: inline-flex;
  }

  .hero {
    padding: 60px 20px;
  }

  .hero h1 {
    font-size: 32px;
  }

  .hero-actions {
    flex-direction: column;
    align-items: center;
  }

  .section {
    padding: 40px 16px;
  }
}
</style>
