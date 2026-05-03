import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'

import Login from './views/Login.vue'
import MainApp from './views/MainApp.vue'

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
