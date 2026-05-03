<template>
  <div class="app-container">
    <!-- 左侧导航栏 -->
    <div class="sidebar">
      <div class="logo">
        <span>🎫</span>
        活动助手
      </div>
      
      <button 
        v-for="item in navItems" 
        :key="item.id"
        :class="['nav-btn', { active: currentPage === item.id }]"
        @click="switchPage(item.id)"
      >
        <span>{{ item.icon }}</span>
        {{ item.name }}
      </button>

      <div style="flex: 1;"></div>
      
      <!-- 访客卡片 -->
      <div v-if="!userStore.token" class="guest-card">
        <div style="font-size: 24px; margin-bottom: 8px;">👤</div>
        <div style="font-size: 14px; color: #666;">访客用户</div>
        <div style="font-size: 12px; color: #888; margin-top: 4px;">体验模式</div>
      </div>

      <!-- 管理员卡片 -->
      <div v-else class="user-info-card">
        <div class="user-avatar">🏢</div>
        <div class="user-name">{{ userStore.userInfo?.organizer_name || '管理员' }}</div>
        <div class="user-role">已登录</div>
      </div>
    </div>

    <!-- 右侧内容区 -->
    <div class="main-content">
      <!-- 顶部信息栏 -->
      <div class="top-bar">
        <div class="weather-card">
          <div class="weather-icon">☀️</div>
          <div class="weather-info">
            <div class="weather-temp">24°C</div>
            <div class="weather-desc">晴 · 空气优</div>
          </div>
        </div>
        <div class="date-info">
          <div class="day">{{ currentDate }}</div>
          <div class="time">{{ currentTime }}</div>
        </div>
      </div>

      <!-- AI 对话页面 -->
      <div v-show="currentPage === 'chat'" class="content-panel chat-page">
        <div class="panel-header">
          <div class="panel-title">
            <span>💬</span>
            智能问答
          </div>
          <div class="panel-subtitle">输入问题，我会帮你查找相关活动信息</div>
        </div>

        <!-- 快捷问题 -->
        <div class="quick-actions">
          <el-button 
            v-for="q in quickQuestions" 
            :key="q"
            class="quick-btn"
            @click="askQuestion(q)"
          >{{ q }}</el-button>
        </div>

        <!-- 消息列表 -->
        <div class="chat-messages" ref="messagesContainer">
          <div 
            v-for="(msg, index) in messages" 
            :key="index"
            :class="['message', msg.type]"
          >
            <div class="message-content">
              <div class="message-label">🤖 助手</div>
              <div class="message-text" v-html="msg.content"></div>
            </div>
          </div>
          <div v-if="loading" class="message assistant">
            <div class="message-content">
              <div class="message-label">🤖 助手</div>
              <div class="message-text">正在思考中...</div>
            </div>
          </div>
        </div>

        <!-- 输入框 -->
        <div class="chat-input-area">
          <input 
            v-model="inputMessage"
            type="text" 
            class="chat-input"
            placeholder="输入你的问题，例如：国际创新博览会在哪里？"
            @keypress="handleKeyPress"
          />
          <button class="send-btn" @click="sendMessage" :disabled="loading">发送</button>
        </div>
      </div>

      <!-- 主办方上传页面 -->
      <div v-show="currentPage === 'organizer'" class="content-panel organizer-page">
        <!-- 登录框 -->
        <div v-if="!userStore.token" class="login-container">
          <div class="login-box">
            <div class="login-icon">🏢</div>
            <div class="login-title">主办方登录</div>
            <div class="login-subtitle">登录后可上传和管理活动信息</div>
            
            <div class="form-group">
              <label class="form-label">用户名 / 手机号</label>
              <input v-model="loginForm.username" type="text" class="form-input" placeholder="请输入账号" />
            </div>
            
            <div class="form-group">
              <label class="form-label">密码</label>
              <input v-model="loginForm.password" type="password" class="form-input" placeholder="请输入密码" @keypress="handleLoginKey" />
            </div>

            <div v-if="loginError" class="error-msg">{{ loginError }}</div>
            
            <button class="login-btn" @click="handleLogin" :loading="loginLoading">登 录</button>
            
            <div class="login-footer">
            </div>
          </div>
        </div>

        <!-- 上传表单 -->
        <div v-else class="upload-container">
          <div class="upload-header">
            <div class="panel-title">
              <span>📤</span>
              活动信息上传
            </div>
            <button class="logout-btn" @click="handleLogout">退出登录</button>
          </div>

          <el-form :model="activityForm" label-width="120px" size="default">
            <!-- 活动基本信息 -->
            <div class="form-section">
              <div class="section-title">
                <span>📋</span>
                活动基本信息
              </div>

              <el-form-item label="活动名称" required>
                <el-input v-model="activityForm.activity_name" placeholder="请输入活动的完整名称" />
              </el-form-item>

              <el-form-item label="活动时间" required>
                <el-date-picker
                  v-model="activityForm.time_range"
                  type="datetimerange"
                  start-placeholder="开始时间"
                  end-placeholder="结束时间"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item label="活动地址" required>
                <el-input v-model="activityForm.address" placeholder="请输入活动详细地址" />
              </el-form-item>

              <el-form-item label="活动简介">
                <el-input v-model="activityForm.description" type="textarea" :rows="3" placeholder="请简要描述活动内容" />
              </el-form-item>

              <el-form-item label="子活动">
                <el-switch v-model="activityForm.has_sub_activities" @change="toggleSubActivities" />
              </el-form-item>

              <div v-if="activityForm.has_sub_activities">
                <div v-for="(sub, index) in activityForm.sub_activities" :key="index" class="sub-activity-item">
                  <div class="sub-activity-header">
                    <span class="sub-activity-title">子活动 {{ index + 1 }}</span>
                    <el-button size="small" type="danger" @click="removeSubActivity(index)">删除</el-button>
                  </div>
                  <el-input v-model="sub.sub_name" placeholder="子活动名称" style="margin-bottom: 10px" />
                  <el-input v-model="sub.location" placeholder="地点" style="margin-bottom: 10px" />
                  <el-input v-model="sub.description" type="textarea" placeholder="简介" :rows="2" />
                </div>
                <el-button style="width: 100%; margin-top: 10px" @click="addSubActivity">➕ 添加子活动</el-button>
              </div>
            </div>

            <!-- 票务信息 -->
            <div class="form-section">
              <div class="section-title">
                <span>🎫</span>
                票务信息
              </div>

              <el-form-item label="需要购票">
                <el-switch v-model="activityForm.requires_ticket" />
              </el-form-item>

              <template v-if="activityForm.requires_ticket">
                <el-form-item label="购票链接">
                  <el-input v-model="activityForm.ticket_url" placeholder="请输入购票网址" />
                </el-form-item>
                <el-form-item label="票价">
                  <el-input v-model="activityForm.ticket_price" placeholder="如：¥99 / 免费" />
                </el-form-item>
                <el-form-item label="购票截止">
                  <el-date-picker v-model="activityForm.ticket_deadline" type="datetime" style="width: 100%" />
                </el-form-item>
              </template>
            </div>

            <!-- 主办方信息 -->
            <div class="form-section">
              <div class="section-title">
                <span>🏢</span>
                主办方信息
              </div>

              <el-form-item label="主办方名称" required>
                <el-input v-model="activityForm.organizer_name" placeholder="企业名称或个人姓名" />
              </el-form-item>
              <el-form-item label="联系电话" required>
                <el-input v-model="activityForm.phone" placeholder="手机号或座机" />
              </el-form-item>
              <el-form-item label="邮箱" required>
                <el-input v-model="activityForm.email" placeholder="联系邮箱" />
              </el-form-item>
            </div>

            <!-- 文件上传 -->
            <div class="form-section">
              <div class="section-title">
                <span>📎</span>
                附件上传
              </div>

              <el-upload
                ref="uploadRef"
                action="#"
                :auto-upload="false"
                :on-change="handleFileChange"
                :on-remove="handleFileRemove"
                multiple
                :limit="10"
              >
                <template #trigger>
                  <div class="upload-area">
                    <div class="upload-icon">📁</div>
                    <div class="upload-text">点击或拖拽文件到此处上传</div>
                    <div class="upload-hint">支持格式：PDF、Word、Excel、TXT 等</div>
                  </div>
                </template>
              </el-upload>

              <div v-if="activityForm.files.length > 0" class="file-list">
                <div v-for="(file, index) in activityForm.files" :key="index" class="file-item">
                  <div class="file-info">
                    <span>📄</span>
                    <span class="file-name">{{ file.name }}</span>
                  </div>
                  <el-button size="small" type="danger" @click="removeFile(index)">删除</el-button>
                </div>
              </div>
            </div>

            <el-button type="primary" style="width: 100%; padding: 20px" size="large" @click="handleSubmit" :loading="submitLoading">
              提 交 信 息
            </el-button>
          </el-form>
        </div>
      </div>

      <!-- 地图导航页面 -->
      <div v-show="currentPage === 'navigation'" class="content-panel navigation-page">
        <div class="panel-header">
          <div class="panel-title">
            <span>🗺️</span>
            会场导航
          </div>
          <div class="panel-subtitle">规划您的出行路线，轻松到达活动现场</div>
        </div>

        <div class="nav-content">
          <div class="map-container">
            <div v-if="!mapLoaded" class="map-placeholder">
              <div class="map-placeholder-icon">🗺️</div>
              <div class="map-placeholder-text">地图展示区域</div>
              <div class="map-placeholder-hint">路线规划功能可用</div>
            </div>
            <div v-else id="amap-container" style="width: 100%; height: 100%; border-radius: 12px;"></div>
          </div>

          <div class="nav-sidebar">
            <!-- 目的地选择 -->
            <div class="nav-card">
              <div class="nav-card-title">📍 选择目的地</div>
              <el-select v-model="navForm.selectedActivity" placeholder="请选择活动" style="width: 100%" @change="onActivitySelect">
                <el-option
                  v-for="act in navActivities"
                  :key="act.id"
                  :label="act.activity_name"
                  :value="act.id"
                />
              </el-select>
              <div v-if="navForm.destination" class="dest-info">
                <strong>{{ navForm.destName }}</strong><br>
                🏠 {{ navForm.destination }}
              </div>
            </div>

            <!-- 起点设置 -->
            <div class="nav-card">
              <div class="nav-card-title">🚩 出发地</div>
              <el-input v-model="navForm.startLocation" placeholder="输入您的出发地址" style="margin-bottom: 10px" />
              <el-button style="width: 100%; margin-bottom: 10px" @click="getLocation" :loading="locating">📍 获取当前位置</el-button>
            </div>

            <!-- 出行方式 -->
            <div class="nav-card">
              <div class="nav-card-title">🚗 出行方式</div>
              <div class="mode-selector">
                <button 
                  v-for="mode in transportModes" 
                  :key="mode.id"
                  :class="['mode-btn', { active: navForm.mode === mode.id }]"
                  @click="navForm.mode = mode.id"
                >
                  <span>{{ mode.icon }}</span>
                  {{ mode.name }}
                </button>
              </div>
              <el-button type="primary" style="width: 100%" @click="planRoute" :loading="planningRoute">🔍 规划路线</el-button>

              <!-- 路线结果 -->
              <div v-if="routeResult" class="route-result">
                <div class="route-summary">
                  <div class="route-stat">
                    <div class="route-stat-value">{{ Math.round(routeResult.duration / 60) }}</div>
                    <div class="route-stat-label">分钟</div>
                  </div>
                  <div class="route-stat">
                    <div class="route-stat-value">{{ (routeResult.distance / 1000).toFixed(1) }}</div>
                    <div class="route-stat-label">公里</div>
                  </div>
                </div>
                <div v-if="routeResult.steps && routeResult.steps.length > 0" class="route-steps">
                  <div v-for="(step, idx) in routeResult.steps.slice(0, 5)" :key="idx" class="route-step">
                    {{ step.instruction || step.name || '' }}
                  </div>
                  <div v-if="routeResult.steps.length > 5" class="route-step-more">...</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { authAPI, activityAPI, chatAPI, navigationAPI } from '@/api'

const userStore = useUserStore()

// 当前页面
const currentPage = ref('chat')

// 导航菜单
const navItems = [
  { id: 'chat', name: '用户查询', icon: '💬' },
  { id: 'organizer', name: '主办方上传', icon: '📤' },
  { id: 'navigation', name: '地图导航', icon: '🗺️' }
]

// 日期时间
const currentDate = ref('')
const currentTime = ref('')

const updateDateTime = () => {
  const now = new Date()
  const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  currentDate.value = `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
  currentTime.value = `${days[now.getDay()]} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  updateDateTime()
  setInterval(updateDateTime, 1000)
  loadNavActivities()
})

// 切换页面
const switchPage = (page) => {
  currentPage.value = page
  if (page === 'navigation') {
    nextTick(() => {
      setTimeout(() => {
        if (!mapInstance) {
          initMap()
        }
      }, 100)
    })
  }
}

// ========== AI 对话 ==========
const messages = ref([
  {
    type: 'assistant',
    content: '您好！我是活动信息智能助手 👋<br><br>我可以帮您查询：<br>• 活动时间、地点<br>• 票价、票务信息<br>• 参展企业介绍<br>• 交通导航路线<br><br>请告诉我您想了解什么？'
  }
])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const chatSessionId = ref(null)

const quickQuestions = [
  '📅 今日活动',
  '📍 博览会地点',
  '🚌 交通路线',
  '💰 票价信息',
  '🏢 参展企业',
  '⏰ 活动时间'
]

const askQuestion = (q) => {
  inputMessage.value = q.replace(/^[📅📍🚌💰🏢⏰]\s*/, '')
  sendMessage()
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const message = inputMessage.value.trim()
  messages.value.push({ type: 'user', content: message })
  inputMessage.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const res = await chatAPI.send({ 
      message,
      session_id: chatSessionId.value || undefined,
    })
    messages.value.push({ type: 'assistant', content: res.data.response })
    if (res.data.session_id) {
      chatSessionId.value = res.data.session_id
    }
  } catch (error) {
    ElMessage.error('发送失败')
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

const handleKeyPress = (e) => {
  if (e.key === 'Enter') sendMessage()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// ========== 登录 ==========
const loginForm = reactive({ username: '', password: '' })
const loginLoading = ref(false)
const loginError = ref('')

const handleLogin = async () => {
  loginLoading.value = true
  loginError.value = ''
  
  try {
    const res = await authAPI.login(loginForm)
    userStore.setToken(res.data.access_token)
    userStore.setUserInfo(res.data.user_info)
    ElMessage.success('登录成功')
  } catch (error) {
    loginError.value = error.response?.data?.detail || '登录失败'
  } finally {
    loginLoading.value = false
  }
}

const handleLoginKey = (e) => {
  if (e.key === 'Enter') handleLogin()
}

const handleLogout = () => {
  userStore.logout()
  loginForm.username = ''
  loginForm.password = ''
  ElMessage.info('已退出登录')
}

// ========== 活动表单 ==========
const activityForm = reactive({
  activity_name: '',
  time_range: [],
  address: '',
  description: '',
  has_sub_activities: false,
  sub_activities: [],
  requires_ticket: false,
  ticket_url: '',
  ticket_price: '',
  ticket_deadline: null,
  organizer_name: '',
  phone: '',
  email: '',
  files: []
})

const toggleSubActivities = () => {
  if (activityForm.has_sub_activities && activityForm.sub_activities.length === 0) {
    addSubActivity()
  }
}

const addSubActivity = () => {
  activityForm.sub_activities.push({ sub_name: '', location: '', description: '' })
}

const removeSubActivity = (index) => {
  activityForm.sub_activities.splice(index, 1)
}

const handleFileChange = (file) => {
  activityForm.files.push(file)
}

const handleFileRemove = (file, index) => {
  activityForm.files.splice(index, 1)
}

const removeFile = (index) => {
  activityForm.files.splice(index, 1)
}

const submitLoading = ref(false)

const handleSubmit = async () => {
  if (!activityForm.activity_name || !activityForm.address) {
    ElMessage.error('请填写活动名称和地址')
    return
  }

  submitLoading.value = true
  
  try {
    const [start_time, end_time] = activityForm.time_range
    
    const data = {
      activity_name: activityForm.activity_name,
      start_time,
      end_time,
      address: activityForm.address,
      description: activityForm.description,
      requires_ticket: activityForm.requires_ticket,
      ticket_url: activityForm.ticket_url,
      ticket_price: activityForm.ticket_price,
      ticket_deadline: activityForm.ticket_deadline,
      status: 1
    }

    await activityAPI.create(data)
    
    // 如果有子活动，逐个创建
    if (activityForm.has_sub_activities) {
      // TODO: 调用子活动 API
    }

    ElMessage.success('提交成功！')
    // 重置表单
    Object.assign(activityForm, {
      activity_name: '',
      time_range: [],
      address: '',
      description: '',
      has_sub_activities: false,
      sub_activities: [],
      requires_ticket: false,
      ticket_url: '',
      ticket_price: '',
      ticket_deadline: null,
      files: []
    })
  } catch (error) {
    ElMessage.error('提交失败：' + (error.response?.data?.detail || '未知错误'))
  } finally {
    submitLoading.value = false
  }
}

// ========== 地图导航 ==========
const navForm = reactive({
  selectedActivity: null,
  destName: '',
  destination: '',
  destCoord: '',
  startLocation: '',
  startCoord: '',
  mode: 'driving'
})

const transportModes = [
  { id: 'driving', name: '驾车', icon: '🚗' },
  { id: 'transit', name: '公交', icon: '🚇' },
  { id: 'walking', name: '步行', icon: '🚶' }
]

const routeResult = ref(null)
const navActivities = ref([])
const locating = ref(false)
const planningRoute = ref(false)
const mapLoaded = ref(false)
let mapInstance = null
let markerInstance = null

const loadNavActivities = async () => {
  try {
    const res = await activityAPI.list({ page: 1, page_size: 100 })
    navActivities.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    console.error('加载活动失败', error)
    navActivities.value = []
  }
}

const onActivitySelect = async (activityId) => {
  const activity = navActivities.value.find(a => a.id === activityId)
  if (activity) {
    navForm.destName = activity.activity_name
    navForm.destination = activity.address
    try {
      const res = await navigationAPI.geocode(activity.address)
      navForm.destCoord = res.data.location
      showMarkerOnMap(res.data.location, activity.activity_name)
    } catch (error) {
      ElMessage.error('地址解析失败')
    }
  }
}

const showMarkerOnMap = (coord, title) => {
  if (!window.AMap || !mapInstance) return
  const [lng, lat] = coord.split(',')
  const position = new window.AMap.LngLat(parseFloat(lng), parseFloat(lat))
  
  mapInstance.setCenter(position)
  
  if (markerInstance) {
    markerInstance.setPosition(position)
  } else {
    markerInstance = new window.AMap.Marker({
      position: position,
      title: title
    })
    mapInstance.add(markerInstance)
  }
}

const initMap = () => {
  if (!window.AMap) {
    console.warn('高德地图 JS API 未加载，地图功能不可用')
    mapLoaded.value = false
    return
  }
  
  mapLoaded.value = true
  nextTick(() => {
    mapInstance = new window.AMap.Map('amap-container', {
      zoom: 12,
      center: [121.473701, 31.230416]
    })
  })
}

const getLocation = () => {
  if (!navigator.geolocation) {
    ElMessage.error('浏览器不支持定位')
    return
  }
  
  locating.value = true
  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      navForm.startCoord = `${pos.coords.longitude.toFixed(6)},${pos.coords.latitude.toFixed(6)}`
      navForm.startLocation = `当前位置 (${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)})`
      locating.value = false
      ElMessage.success('已获取当前位置')
    },
    async () => {
      locating.value = false
      if (navForm.startLocation) {
        try {
          const res = await navigationAPI.geocode(navForm.startLocation)
          navForm.startCoord = res.data.location
          ElMessage.success('地址解析成功')
        } catch (error) {
          ElMessage.error('无法获取位置，请检查地址')
        }
      } else {
        ElMessage.error('无法获取位置，请手动输入地址')
      }
    }
  )
}

const planRoute = async () => {
  if (!navForm.startCoord && !navForm.startLocation) {
    ElMessage.warning('请输入或获取出发地')
    return
  }
  if (!navForm.destCoord) {
    ElMessage.warning('请选择目的地活动')
    return
  }
  
  planningRoute.value = true
  
  try {
    let origin = navForm.startCoord
    if (!origin && navForm.startLocation) {
      const geoRes = await navigationAPI.geocode(navForm.startLocation)
      origin = geoRes.data.location
    }
    
    const res = await navigationAPI.planRoute(origin, navForm.destCoord, navForm.mode)
    routeResult.value = res.data
    
    drawRouteOnMap(res.data)
    ElMessage.success('路线规划成功')
  } catch (error) {
    ElMessage.error('路线规划失败：' + (error.response?.data?.detail || '未知错误'))
  } finally {
    planningRoute.value = false
  }
}

const drawRouteOnMap = (routeData) => {
  if (!window.AMap || !mapInstance) return
  
  if (window.routeLine) {
    mapInstance.remove(window.routeLine)
  }
  
  if (routeData.polyline) {
    const path = routeData.polyline.split(';').map(p => {
      const [lng, lat] = p.split(',')
      return [parseFloat(lng), parseFloat(lat)]
    })
    window.routeLine = new window.AMap.Polyline({
      path: path,
      strokeColor: '#667eea',
      strokeWeight: 6,
      strokeOpacity: 0.8
    })
    mapInstance.add(window.routeLine)
    mapInstance.setFitView([window.routeLine])
  }
}

</script>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  gap: 20px;
  background: #faf8f5;
}

/* 左侧导航栏 */
.sidebar {
  width: 260px;
  background: white;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  border: 1px solid #eee;
}

.logo {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-btn {
  width: 100%;
  padding: 14px 20px;
  border: none;
  background: #f8f9fa;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  margin-bottom: 10px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 12px;
  text-align: left;
}

.nav-btn:hover {
  background: #e9ecef;
  transform: translateX(5px);
}

.nav-btn.active {
  background: #2c3e50;
  color: white;
}

.guest-card {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  text-align: center;
}

.user-info-card {
  padding: 16px;
  background: #2c3e50;
  border-radius: 12px;
  text-align: center;
  color: white;
}

.user-avatar {
  font-size: 32px;
  margin-bottom: 8px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
}

.user-role {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 4px;
}

/* 右侧内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 顶部信息栏 */
.top-bar {
  background: white;
  border-radius: 20px;
  padding: 20px 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #eee;
}

.weather-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 20px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #eee;
}

.weather-icon {
  font-size: 32px;
}

.weather-temp {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.weather-desc {
  font-size: 13px;
  color: #888;
}

.date-info {
  text-align: right;
  color: #666;
}

.date-info .day {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.date-info .time {
  font-size: 14px;
  color: #888;
}

/* 内容面板 */
.content-panel {
  background: white;
  border-radius: 20px;
  flex: 1;
  padding: 28px;
  border: 1px solid #eee;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  margin-bottom: 24px;
}

.panel-title {
  font-size: 22px;
  font-weight: 700;
  color: #333;
  display: flex;
  align-items: center;
  gap: 10px;
}

.panel-subtitle {
  font-size: 14px;
  color: #888;
  margin-top: 6px;
}

/* AI 对话页面 */
.chat-page {
  height: calc(100vh - 160px);
}

.quick-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.quick-btn {
  padding: 10px 18px;
  background: #f0f4ff;
  border: 1px solid #d1d9f0;
  border-radius: 20px;
  font-size: 13px;
  color: #667eea;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: #2c3e50;
  color: white;
  border-color: #2c3e50;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
  margin-bottom: 20px;
}

.message {
  margin-bottom: 16px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.user {
  display: flex;
  justify-content: flex-end;
}

.message-content {
  max-width: 75%;
  padding: 14px 18px;
  border-radius: 16px;
  line-height: 1.6;
}

.message.user .message-content {
  background: #2c3e50;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-content {
  background: #f1f3f5;
  color: #333;
  border-bottom-left-radius: 4px;
}

.message-label {
  font-size: 12px;
  color: #888;
  margin-bottom: 6px;
}

.message-text {
  line-height: 1.6;
}

.chat-input-area {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.chat-input {
  flex: 1;
  padding: 16px 20px;
  border: 2px solid #e9ecef;
  border-radius: 16px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input:focus {
  border-color: #2c3e50;
}

.send-btn {
  padding: 16px 28px;
  background: #2c3e50;
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.send-btn:hover {
  background: #34495e;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 主办方上传页面 */
.organizer-page {
  height: calc(100vh - 160px);
  overflow-y: auto;
}

.login-container {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
}

.login-box {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 20px;
  text-align: center;
  border: 1px solid #eee;
}

.login-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.login-title {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 14px;
  color: #888;
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
  text-align: left;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #555;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #2c3e50;
}

.login-btn {
  width: 100%;
  padding: 16px;
  background: #2c3e50;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 10px;
  transition: background 0.2s;
}

.login-btn:hover {
  background: #34495e;
}

.login-footer {
  margin-top: 24px;
  font-size: 13px;
  color: #888;
}

.error-msg {
  color: #dc3545;
  font-size: 13px;
  margin-top: -10px;
  margin-bottom: 15px;
}

.upload-container {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
}

.upload-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.logout-btn {
  padding: 10px 20px;
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #dc3545;
  color: white;
  border-color: #dc3545;
}

.form-section {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  border: 1px solid #eee;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.sub-activity-item {
  background: white;
  border: 2px dashed #d1d9f0;
  border-radius: 12px;
  padding: 16px;
  margin-top: 12px;
}

.sub-activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.sub-activity-title {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.upload-area {
  border: 2px dashed #d1d9f0;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  transition: all 0.2s;
  cursor: pointer;
}

.upload-area:hover {
  border-color: #2c3e50;
  background: #fafafa;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 15px;
  color: #666;
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 12px;
  color: #999;
}

.file-list {
  margin-top: 16px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: white;
  border-radius: 8px;
  margin-bottom: 8px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-name {
  font-size: 13px;
  color: #333;
}

/* 地图导航页面 */
.navigation-page {
  height: calc(100vh - 160px);
}

.nav-content {
  flex: 1;
  display: flex;
  gap: 20px;
}

.map-container {
  flex: 1;
  background: #e9ecef;
  border-radius: 16px;
  position: relative;
  overflow: hidden;
}

.map-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  color: #666;
}

.map-placeholder-icon {
  font-size: 80px;
  margin-bottom: 16px;
}

.map-placeholder-text {
  font-size: 18px;
  font-weight: 600;
}

.map-placeholder-hint {
  font-size: 14px;
  color: #999;
  margin-top: 8px;
}

.nav-sidebar {
  width: 340px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dest-card, .nav-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #eee;
}

.dest-title, .nav-card-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.dest-info {
  font-size: 13px;
  color: #666;
  line-height: 1.8;
}

.location-input-group {
  margin-bottom: 14px;
}

.location-label {
  font-size: 12px;
  color: #888;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.location-input {
  width: 100%;
  padding: 12px 14px;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.location-input:focus {
  border-color: #2c3e50;
}

.mode-selector {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.mode-btn {
  flex: 1;
  padding: 12px;
  border: 2px solid #e9ecef;
  background: white;
  border-radius: 10px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.mode-btn:hover {
  border-color: #2c3e50;
}

.mode-btn.active {
  border-color: #2c3e50;
  background: #f5f5f5;
  color: #2c3e50;
}

.mode-btn span:first-child {
  font-size: 22px;
}

.route-result {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-top: 12px;
  display: none;
}

.route-result.show {
  display: block;
}

.route-summary {
  display: flex;
  gap: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.route-stat {
  text-align: center;
}

.route-stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
}

.route-stat-label {
  font-size: 12px;
  color: #888;
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f3f5;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #ced4da;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #adb5bd;
}
</style>
