<template>
  <div class="home-page">
    <!-- 顶部导航 -->
    <header class="navbar">
      <div class="logo" @click="$router.push('/home')">🎯 会场精灵</div>
      <div class="nav-links">
        <el-button text @click="$router.push('/home')">首页</el-button>
        <el-button text @click="$router.push('/activities')">活动列表</el-button>
        <el-button text @click="$router.push('/chat')">AI 助手</el-button>
        <el-button v-if="!userStore.token" type="primary" @click="$router.push('/login')">主办方登录</el-button>
        <el-button v-else type="danger" @click="handleLogout">退出</el-button>
      </div>
    </header>

    <!-- Hero 区域 -->
    <section class="hero">
      <h1>探索精彩活动</h1>
      <p>汇聚各类精彩活动，AI 智能助手随时为您解答</p>
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="搜索活动名称、地点..."
          size="large"
          prefix-icon="Search"
          clearable
          style="max-width: 500px"
        >
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </div>
    </section>

    <!-- 热门活动 -->
    <section class="section">
      <div class="container">
        <h2>📅 近期活动</h2>
        <el-tabs v-model="statusFilter">
          <el-tab-pane label="即将开始" name="upcoming"></el-tab-pane>
          <el-tab-pane label="进行中" name="ongoing"></el-tab-pane>
        </el-tabs>
        
        <el-row :gutter="20">
          <el-col 
            v-for="act in filteredActivities" 
            :key="act.id" 
            :xs="24" :sm="12" :md="8"
            style="margin-bottom: 20px"
          >
            <el-card shadow="hover" class="activity-card">
              <h3>{{ act.activity_name }}</h3>
              <p class="time">{{ formatDate(act.start_time) }} - {{ formatDate(act.end_time) }}</p>
              <p class="address">📍 {{ act.address }}</p>
              <div class="tags">
                <el-tag size="small" v-for="tag in ['科技', '创新']" :key="tag">{{ tag }}</el-tag>
              </div>
              <el-button link type="primary" @click="$router.push('/activities/' + act.id)">查看详情</el-button>
            </el-card>
          </el-col>
        </el-row>
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { activityAPI } from '@/api'

const router = useRouter()
const userStore = useUserStore()

const searchQuery = ref('')
const statusFilter = ref('upcoming')
const activities = ref([])

const filteredActivities = computed(() => {
  // 这里可以加过滤逻辑
  return activities.value.slice(0, 6)
})

const handleSearch = () => {
  if (searchQuery.value) {
    router.push({ path: '/activities', query: { q: searchQuery.value } })
  } else {
    router.push('/activities')
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const handleLogout = () => {
  userStore.logout()
  location.reload()
}

// 加载活动数据
activityAPI.list().then(res => {
  activities.value = res.data
}).catch(console.error)
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

.search-box {
  display: flex;
  justify-content: center;
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
</style>
