<template>
  <div class="chat-page">
    <div class="chat-container">
      <div class="chat-header">
        <h2>🤖 AI 智能助手</h2>
        <el-select v-model="selectedActivity" placeholder="选择关联活动" clearable style="width: 200px">
          <el-option
            v-for="act in activities"
            :key="act.id"
            :label="act.activity_name"
            :value="act.id"
          />
        </el-select>
      </div>

      <!-- 消息列表 -->
      <div class="messages-container" ref="messagesContainer">
        <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.type]">
          <div class="message-avatar">
            {{ msg.type === 'user' ? '👤' : '🤖' }}
          </div>
          <div class="message-content">
            <div class="message-label">{{ msg.type === 'user' ? '你' : 'AI 助手' }}</div>
            <div class="message-text" v-html="msg.content"></div>
          </div>
        </div>
        <div v-if="loading" class="message assistant">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <div class="message-label">AI 助手</div>
            <div class="message-text">正在思考中...</div>
          </div>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="input-container">
        <!-- 快捷问题 -->
        <div class="quick-actions">
          <el-button size="small" round @click="askQuick('今天的活动有哪些？')">今天的活动有哪些？</el-button>
          <el-button size="small" round @click="askQuick('活动在哪里？')">活动在哪里？</el-button>
          <el-button size="small" round @click="askQuick('门票多少钱？')">门票多少钱？</el-button>
          <el-button size="small" round @click="askQuick('怎么去？')">怎么去？</el-button>
        </div>

        <div class="input-box">
          <el-input
            v-model="inputMessage"
            placeholder="输入你的问题..."
            @keyup.enter="sendMessage"
            :disabled="loading"
          >
            <template #append>
              <el-button @click="sendMessage" :loading="loading">
                <el-icon><Promotion /></el-icon>
              </el-button>
            </template>
          </el-input>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { chatAPI, activityAPI } from '@/api'
import { Promotion } from '@element-plus/icons-vue'

const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const selectedActivity = ref(null)
const activities = ref([])
const sessionId = ref(null)
const messagesContainer = ref(null)

const askQuick = (question) => {
  inputMessage.value = question
  sendMessage()
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const message = inputMessage.value.trim()
  inputMessage.value = ''

  // 添加用户消息
  messages.value.push({
    type: 'user',
    content: message,
  })

  loading.value = true
  scrollToBottom()

  try {
    const res = await chatAPI.send({
      message: message,
      activity_id: selectedActivity.value,
      session_id: sessionId.value,
    })

    sessionId.value = res.data.session_id

    messages.value.push({
      type: 'assistant',
      content: res.data.response,
    })
  } catch (error) {
    ElMessage.error('发送失败')
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const loadActivities = async () => {
  try {
    const res = await activityAPI.list({ page: 1, page_size: 100 })
    activities.value = res.data
  } catch (error) {
    console.error('加载活动列表失败', error)
  }
}

onMounted(() => {
  loadActivities()
})
</script>

<style scoped>
.chat-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-container {
  background: white;
  border-radius: 20px;
  padding: 30px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  display: flex;
  gap: 15px;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.assistant {
  align-self: flex-start;
}

.message-avatar {
  font-size: 32px;
  flex-shrink: 0;
}

.message-content {
  background: #f0f4ff;
  padding: 15px 20px;
  border-radius: 12px;
}

.message.user .message-content {
  background: #667eea;
  color: white;
}

.message-label {
  font-size: 12px;
  color: #999;
  margin-bottom: 5px;
}

.message.user .message-label {
  color: rgba(255, 255, 255, 0.8);
}

.message-text {
  line-height: 1.6;
}

.input-container {
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.quick-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.input-box {
  display: flex;
  gap: 10px;
}
</style>
