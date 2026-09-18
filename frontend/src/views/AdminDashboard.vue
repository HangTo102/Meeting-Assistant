<template>
  <div class="admin-layout">
    <!-- 顶部导航 -->
    <header class="admin-header">
      <div class="header-left">
        <div class="logo" @click="$router.push('/home')">🎯 会场精灵</div>
        <el-button text @click="$router.push('/admin/activities')">我的活动</el-button>
        <el-button text @click="$router.push('/admin/activities/create')">创建活动</el-button>
      </div>
      <div class="header-right">
        <span class="user-name">{{ userStore.userInfo?.organizer_name }}</span>
        <el-button link type="danger" @click="handleLogout">退出登录</el-button>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="admin-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const handleLogout = () => {
  userStore.logout()
  router.push('/home')
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: #faf8f5;
  display: flex;
  flex-direction: column;
}

.admin-header {
  background: white;
  border-bottom: 1px solid #eee;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  color: #667eea;
  cursor: pointer;
  margin-right: 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-name {
  font-size: 14px;
  color: #666;
}

.admin-main {
  flex: 1;
  padding: 24px;
  min-width: 0;
}

@media (max-width: 768px) {
  .admin-header {
    padding: 0 12px;
    height: auto;
    min-height: 56px;
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-left {
    flex-wrap: wrap;
    gap: 8px;
  }

  .logo {
    margin-right: 8px;
  }

  .admin-main {
    padding: 12px;
  }
}
</style>
