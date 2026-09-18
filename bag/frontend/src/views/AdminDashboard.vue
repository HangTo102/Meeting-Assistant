<template>
  <div class="admin-dashboard">
    <!-- 移动端顶部栏 -->
    <div class="mobile-header">
      <div class="logo" @click="$router.push('/home')">会场精灵</div>
      <el-button text @click="menuVisible = true">
        <el-icon :size="24"><Menu /></el-icon>
      </el-button>
    </div>

    <!-- 侧边栏（桌面端固定，移动端抽屉） -->
    <div class="sidebar" :class="{ open: menuVisible }">
      <div class="sidebar-inner">
        <div class="logo desktop-only" @click="$router.push('/home')">↩️ 返回首页</div>
        <div class="mobile-close">
          <el-button text @click="menuVisible = false">
            <el-icon :size="20"><Close /></el-icon>
          </el-button>
        </div>
        <el-menu :default-active="activeMenu" class="nav-menu" @select="menuVisible = false">
          <el-menu-item index="/admin/activities">
            <el-icon><Calendar /></el-icon>
            <span>我的活动</span>
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
    </div>

    <!-- 遮罩 -->
    <div v-if="menuVisible" class="sidebar-overlay" @click="menuVisible = false"></div>

    <!-- 主内容区 -->
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Calendar, Plus, Menu, Close } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const menuVisible = ref(false)

const activeMenu = computed(() => {
  if (route.path.startsWith('/admin/activities/create')) return '/admin/activities/create'
  if (route.path.startsWith('/admin/activities/')) return '/admin/activities'
  return route.path
})

const handleLogout = () => {
  userStore.logout()
  router.push('/home')
}
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  min-height: 100vh;
  background: #faf8f5;
}

.sidebar {
  width: 240px;
  background: white;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
}

.mobile-header {
  display: none;
}

.mobile-close {
  display: none;
}

.logo {
  font-size: 18px;
  font-weight: bold;
  color: #667eea;
  padding: 10px 0 20px;
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
  font-size: 14px;
}

.main-content {
  flex: 1;
  padding: 30px;
  min-width: 0;
}

@media (max-width: 768px) {
  .admin-dashboard {
    flex-direction: column;
  }

  .mobile-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: white;
    border-bottom: 1px solid #eee;
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 200;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    box-shadow: 2px 0 8px rgba(0,0,0,0.1);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .mobile-close {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 10px;
  }

  .desktop-only {
    display: none;
  }

  .sidebar-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.4);
    z-index: 150;
  }

  .main-content {
    padding: 16px;
  }
}
</style>
