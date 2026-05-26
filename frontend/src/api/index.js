import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  maxRedirects: 0,
})

// 请求拦截器：添加 Token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理错误
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ========== 认证 API ==========
export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  getCurrentUser: () => api.get('/auth/me'),
}

// ========== 活动 API ==========
export const activityAPI = {
  list: (params) => api.get('/activities', { params }),
  get: (id) => api.get(`/activities/${id}`),
  create: (data) => api.post('/activities', data),
  update: (id, data) => api.put(`/activities/${id}`, data),
  delete: (id) => api.delete(`/activities/${id}`),
  search: (q) => api.get('/activities/search', { params: { q } }),
}

// ========== 子活动 API ==========
export const subActivityAPI = {
  list: (activityId) => api.get(`/sub-activities/activity/${activityId}`),
  create: (data) => api.post('/sub-activities', data),
  update: (id, data) => api.put(`/sub-activities/${id}`, data),
  delete: (id) => api.delete(`/sub-activities/${id}`),
}

// ========== 标签 API ==========
export const tagAPI = {
  list: (activityId) => api.get(`/tags/activity/${activityId}`),
  create: (data) => api.post('/tags', data),
  delete: (id) => api.delete(`/tags/${id}`),
  getAll: () => api.get('/tags/all'),
}

// ========== AI 对话 API ==========
export const chatAPI = {
  send: (data) => api.post('/chat', data),
  getHistory: (sessionId) => api.get(`/chat/history/${sessionId}`),
}

// ========== 文件上传 API ==========
export const uploadAPI = {
  upload: (file, activityId = null) => {
    const formData = new FormData()
    formData.append('file', file)
    if (activityId) {
      formData.append('activity_id', activityId)
    }
    return api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  get: (fileId) => api.get(`/upload/${fileId}`, { responseType: 'blob' }),
  delete: (fileId) => api.delete(`/upload/${fileId}`),
}

// ========== 地图导航 API ==========
export const navigationAPI = {
  planRoute: (origin, destination, mode) => 
    api.get('/navigation/route', { params: { origin, destination, mode } }),
  geocode: (address) => 
    api.get('/navigation/geocode', { params: { address } }),
}

export default api
