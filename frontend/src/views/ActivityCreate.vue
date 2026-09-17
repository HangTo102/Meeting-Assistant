<template>
  <div class="activity-create">
    <el-page-header @back="$router.back()" :title="isEdit ? '编辑活动' : '创建活动'" />

    <el-card style="margin-top: 20px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
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

        <el-form-item label="活动标签">
          <el-tag
            v-for="(tag, index) in form.tags"
            :key="index"
            closable
            @close="removeTag(index)"
            style="margin-right: 8px; margin-bottom: 8px"
          >
            {{ tag }}
          </el-tag>
          <el-input
            v-if="tagInputVisible"
            ref="tagInputRef"
            v-model="tagInputValue"
            size="small"
            style="width: 100px"
            @keyup.enter="confirmTag"
            @blur="confirmTag"
          />
          <el-button v-else size="small" @click="showTagInput">+ 添加标签</el-button>
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
          <el-form-item label="购票截止">
            <el-date-picker v-model="form.ticket_deadline" type="datetime" style="width: 100%" />
          </el-form-item>
        </template>

        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :label="0">草稿</el-radio>
            <el-radio :label="1">已发布</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 子活动 -->
        <div class="section">
          <div class="section-title">子活动 / 分会场</div>
          <div v-for="(sub, index) in form.sub_activities" :key="sub.id || index" class="sub-item">
            <div class="sub-header">
              <span>子活动 {{ index + 1 }}</span>
              <el-button size="small" type="danger" @click="removeSub(index)">删除</el-button>
            </div>
            <el-form-item label="名称">
              <el-input v-model="sub.sub_name" placeholder="子活动名称" />
            </el-form-item>
            <el-form-item label="时间">
              <el-date-picker
                v-model="sub.time_range"
                type="datetimerange"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="地点">
              <el-input v-model="sub.location" placeholder="地点" />
            </el-form-item>
            <el-form-item label="简介">
              <el-input v-model="sub.description" type="textarea" :rows="2" placeholder="简介" />
            </el-form-item>
          </div>
          <el-button style="width: 100%" @click="addSub">+ 添加子活动</el-button>
        </div>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">{{ isEdit ? '保存' : '提交' }}</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { activityAPI, subActivityAPI, tagAPI } from '@/api'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const formRef = ref(null)

const isEdit = ref(false)
const activityId = ref(null)

const form = reactive({
  activity_name: '',
  time_range: [],
  address: '',
  description: '',
  tags: [],
  requires_ticket: false,
  ticket_price: '',
  ticket_url: '',
  ticket_deadline: null,
  status: 1,
  sub_activities: []
})

const rules = {
  activity_name: [{ required: true, message: '请输入活动名称', trigger: 'blur' }],
  time_range: [{ required: true, message: '请选择活动时间', trigger: 'change' }],
  address: [{ required: true, message: '请输入活动地点', trigger: 'blur' }]
}

const tagInputVisible = ref(false)
const tagInputValue = ref('')
const tagInputRef = ref(null)

const showTagInput = () => {
  tagInputVisible.value = true
  nextTick(() => tagInputRef.value?.focus())
}

const confirmTag = () => {
  const val = tagInputValue.value.trim()
  if (val && !form.tags.includes(val)) {
    form.tags.push(val)
  }
  tagInputValue.value = ''
  tagInputVisible.value = false
}

const removeTag = (index) => form.tags.splice(index, 1)

const addSub = () => {
  form.sub_activities.push({ sub_name: '', time_range: [], location: '', description: '' })
}

const removeSub = (index) => form.sub_activities.splice(index, 1)

const toISO = (date) => date ? new Date(date).toISOString() : null

onMounted(async () => {
  const id = route.params.id || route.query.id
  if (id) {
    isEdit.value = true
    activityId.value = Number(id)
    await loadActivity(activityId.value)
  }
})

const loadActivity = async (id) => {
  try {
    const res = await activityAPI.get(id)
    const act = res.data
    Object.assign(form, {
      activity_name: act.activity_name,
      time_range: [new Date(act.start_time), new Date(act.end_time)],
      address: act.address,
      description: act.description || '',
      tags: act.tag_list || [],
      requires_ticket: act.requires_ticket,
      ticket_price: act.ticket_price || '',
      ticket_url: act.ticket_url || '',
      ticket_deadline: act.ticket_deadline ? new Date(act.ticket_deadline) : null,
      status: act.status
    })

    const subsRes = await subActivityAPI.list(id)
    form.sub_activities = subsRes.data.map(sub => ({
      ...sub,
      time_range: sub.start_time && sub.end_time ? [new Date(sub.start_time), new Date(sub.end_time)] : []
    }))
  } catch (error) {
    ElMessage.error('加载活动失败')
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch (e) {
    return
  }

  loading.value = true

  try {
    const [start_time, end_time] = form.time_range

    const data = {
      activity_name: form.activity_name,
      start_time: toISO(start_time),
      end_time: toISO(end_time),
      address: form.address,
      description: form.description || null,
      requires_ticket: form.requires_ticket,
      ticket_price: form.ticket_price || null,
      ticket_url: form.ticket_url || null,
      ticket_deadline: toISO(form.ticket_deadline),
      status: form.status
    }

    let actId = activityId.value
    if (isEdit.value) {
      await activityAPI.update(actId, data)
      ElMessage.success('保存成功')
    } else {
      const res = await activityAPI.create(data)
      actId = res.data.id
      ElMessage.success('创建成功')
    }

    // 保存子活动
    for (const sub of form.sub_activities) {
      const subData = {
        activity_id: actId,
        sub_name: sub.sub_name,
        start_time: toISO(sub.time_range?.[0]),
        end_time: toISO(sub.time_range?.[1]),
        location: sub.location || null,
        description: sub.description || null,
        sort_order: 0
      }
      if (sub.id) {
        await subActivityAPI.update(sub.id, subData)
      } else {
        await subActivityAPI.create(subData)
      }
    }

    // 保存标签（简单策略：删除旧标签，重建新标签）
    if (isEdit.value) {
      const oldTagsRes = await tagAPI.list(actId)
      for (const t of oldTagsRes.data) {
        await tagAPI.delete(t.id)
      }
    }
    for (const tagName of form.tags) {
      await tagAPI.create({ activity_id: actId, tag_name: tagName })
    }

    router.push('/admin/activities')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.activity-create {
  background: white;
  padding: 24px;
  border-radius: 16px;
}
.section {
  background: #fafafa;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}
.section-title {
  font-weight: 600;
  margin-bottom: 16px;
}
.sub-item {
  background: white;
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}
.sub-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 500;
}
@media (max-width: 768px) {
  .activity-create {
    padding: 16px;
    border-radius: 0;
  }
  :deep(.el-form-item__label) {
    float: none;
    display: block;
    text-align: left;
    padding: 0 0 8px;
  }
}
</style>
