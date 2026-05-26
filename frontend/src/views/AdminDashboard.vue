<template>
  <div class="admin-dashboard">
    <!-- 侧边栏 -->
    <div class="sidebar">
      <div class="logo" @click="$router.push('/home')">↩️ 返回首页</div>
      <el-menu :default-active="activeMenu" class="nav-menu">
        <el-menu-item index="/admin">
          <el-icon><HomeFilled /></el-icon>
          <span>管理首页</span>
        </el-menu-item>
        <el-menu-item index="/activities">
          <el-icon><Calendar /></el-icon>
          <span>活动列表</span>
        </el-menu-item>
        <el-menu-item index="/admin/activities/create">
          <el-icon><Plus /></el-icon>
          <span>创建活动</span>
        </el-menu-item>
      </el-menu>
      
      <div class="user-info">
        <el-avatar :size="40">{{ userStore.userInfo?.organizer_name?.[0] || 'U' }}</el-avatar>
        <div class="user-name">{{ userStore.userInfo?.organizer_name }}</div>
        <el-button link type="danger" @click="handleLogout">退出登录</el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HomeFilled, Calendar, Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 240px;
  background: white;
  padding: 20px;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  color: #667eea;
  padding: 20px 10px;
  margin-bottom: 20px;
  cursor: pointer;
}

.nav-menu {
  flex: 1;
  border: none;
}

.user-info {
  padding: 20px 10px;
  border-top: 1px solid #eee;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.user-name {
  font-weight: 500;
}

.main-content {
  flex: 1;
  padding: 30px;
  background: #faf8f5;
}
</style>
