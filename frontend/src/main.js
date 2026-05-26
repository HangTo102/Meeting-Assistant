import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'

import Login from './views/Login.vue'
import MainApp from './views/MainApp.vue'

// 动态加载高德地图 JS SDK
// 认证方式：使用高德开放平台 -> 应用管理 -> 添加 Key -> JS API -> 设置"域名白名单"
// 将你的部署域名加入白名单即可，不需要 securityJsCode
// 如果确实使用 securityJsCode 方式，请在 frontend/.env 中设置 VITE_AMAP_SECURITY_CODE
const amapKey = import.meta.env.VITE_AMAP_KEY || ''
const amapSecurityCode = import.meta.env.VITE_AMAP_SECURITY_CODE || ''
if (amapKey) {
  if (amapSecurityCode) {
    window._AMapSecurityConfig = { securityJsCode: amapSecurityCode }
  }
  const script = document.createElement('script')
  script.src = `https://webapi.amap.com/maps?v=2.0&key=${amapKey}`
  script.onload = () => {
    window.__amapReady = true
    window.dispatchEvent(new CustomEvent('amap-ready'))
  }
  document.head.appendChild(script)
} else {
  console.warn('未配置 VITE_AMAP_KEY，地图功能不可用')
}

const routes = [
  { path: '/', redirect: '/app' },
  { path: '/login', name: 'Login', component: Login },
  { path: '/app', name: 'MainApp', component: MainApp },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')
