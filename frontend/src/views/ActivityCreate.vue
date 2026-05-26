<template>
  <div class="activity-create">
    <el-page-header @back="$router.back()" title="创建活动" />
    
    <el-card style="margin-top: 20px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="活动名称" prop="activity_name">
          <el-input v-model="form.activity_name" placeholder="请输入活动完整名称" />
        </el-form-item>
        
        <el-form-item label="活动时间" prop="time_range">
          <el-date-picker
            v-model="form.time_range"
            type="datetimerange"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="活动地点" prop="address">
          <el-input v-model="form.address" placeholder="请输入详细活动地点" />
        </el-form-item>
        
        <el-form-item label="活动简介" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请简要描述活动内容" />
        </el-form-item>
        
        <el-form-item label="是否需要购票">
          <el-switch v-model="form.requires_ticket" />
        </el-form-item>
        
        <template v-if="form.requires_ticket">
          <el-form-item label="票价信息">
            <el-input v-model="form.ticket_price" placeholder="例如：早鸟票 ¥99, 普通票 ¥149" />
          </el-form-item>
          <el-form-item label="购票链接">
            <el-input v-model="form.ticket_url" placeholder="https://..." />
          </el-form-item>
          <el-form-item label="购票截止时间">
            <el-date-picker v-model="form.ticket_deadline" type="datetime" style="width: 100%" />
          </el-form-item>
        </template>
        
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :label="0">草稿</el-radio>
            <el-radio :label="1">已发布</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">提交</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { activityAPI } from '@/api'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const formRef = ref(null)

const form = reactive({
  activity_name: '',
  time_range: [],
  address: '',
  description: '',
  requires_ticket: false,
  ticket_price: '',
  ticket_url: '',
  ticket_deadline: null,
  status: 1,
})

const rules = {
  activity_name: [{ required: true, message: '请输入活动名称', trigger: 'blur' }],
  time_range: [{ required: true, message: '请选择活动时间', trigger: 'change' }],
  address: [{ required: true, message: '请输入活动地点', trigger: 'blur' }],
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    loading.value = true
    
    const [start_time, end_time] = form.time_range
    
    const data = {
      activity_name: form.activity_name,
      start_time: start_time.toISOString(),
      end_time: end_time.toISOString(),
      address: form.address,
      description: form.description || null,
      requires_ticket: form.requires_ticket,
      ticket_price: form.ticket_price || null,
      ticket_url: form.ticket_url || null,
      ticket_deadline: form.ticket_deadline ? form.ticket_deadline.toISOString() : null,
      status: form.status,
    }
    
    await activityAPI.create(data)
    
    ElMessage.success('创建成功')
    router.push('/activities')
  } catch (error) {
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.activity-create {
  background: white;
  padding: 30px;
  border-radius: 20px;
}
</style>
