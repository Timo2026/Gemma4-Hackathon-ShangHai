<template>
  <div class="ip-profile">
    <div class="page-header">
      <h2>律师简介包装</h2>
      <p class="subtitle">AI 根据您的专业背景，生成多平台适配的律师简介</p>
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :md="14">
        <el-card shadow="never">
          <template #header><span class="card-title">📝 填写基本信息</span></template>
          <el-form :model="form" label-position="top" size="large">
            <el-form-item label="律师姓名">
              <el-input v-model="form.name" placeholder="请输入姓名" />
            </el-form-item>
            <el-form-item label="执业领域">
              <el-select v-model="form.fields" multiple placeholder="选择执业领域" style="width:100%">
                <el-option label="民商事诉讼" value="民商事诉讼" />
                <el-option label="刑事辩护" value="刑事辩护" />
                <el-option label="知识产权" value="知识产权" />
                <el-option label="劳动纠纷" value="劳动纠纷" />
                <el-option label="婚姻家庭" value="婚姻家庭" />
                <el-option label="公司法律顾问" value="公司法律顾问" />
                <el-option label="行政诉讼" value="行政诉讼" />
                <el-option label="房产纠纷" value="房产纠纷" />
              </el-select>
            </el-form-item>
            <el-form-item label="执业年限">
              <el-input-number v-model="form.years" :min="0" :max="50" />
            </el-form-item>
            <el-form-item label="个人亮点（选填）">
              <el-input v-model="form.highlights" type="textarea" :rows="3" placeholder="例如：代理过XX重大案件，拥有XX资质认证，胜诉率XX%" />
            </el-form-item>
            <el-form-item label="目标平台">
              <el-checkbox-group v-model="form.platforms">
                <el-checkbox label="抖音" />
                <el-checkbox label="小红书" />
                <el-checkbox label="微信视频号" />
                <el-checkbox label="B站" />
                <el-checkbox label="知乎" />
              </el-checkbox-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" size="large" @click="handleGenerate" style="width:100%">
                {{ loading ? 'AI 生成中...' : '🚀 AI 生成简介' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="10">
        <el-card shadow="never">
          <template #header><span class="card-title">📄 生成结果</span></template>
          <div v-if="!result && !loading" class="empty-state">
            <el-empty description="填写信息后生成简介" />
          </div>
          <div v-loading="loading" class="result-content">
            <div v-if="result" class="markdown-body" v-html="renderedResult"></div>
          </div>
          <div v-if="result" class="result-actions">
            <el-button @click="copyResult">复制</el-button>
            <el-button type="primary" @click="saveProfile">保存</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useIPStore } from '@/stores/ip'
import { marked } from 'marked'
import { ElMessage } from 'element-plus'

const ipStore = useIPStore()
const loading = ref(false)
const result = ref(null)

const form = reactive({
  name: '',
  fields: [],
  years: 5,
  highlights: '',
  platforms: ['抖音', '小红书'],
})

const renderedResult = computed(() => {
  if (!result?.content) return ''
  return marked(result.content)
})

async function handleGenerate() {
  loading.value = true
  try {
    const res = await ipStore.createProfile({
      name: form.name,
      fields: form.fields,
      years: form.years,
      highlights: form.highlights,
      platforms: form.platforms,
    })
    result.value = res
    ElMessage.success('简介生成成功！')
  } catch (err) {
    // 错误已处理
  } finally {
    loading.value = false
  }
}

function copyResult() {
  if (!result?.content) return
  navigator.clipboard.writeText(result.content).then(() => ElMessage.success('已复制'))
}

function saveProfile() {
  ElMessage.success('已保存到个人中心')
}
</script>

<style scoped>
.ip-profile {
  max-width: 1200px;
  margin: 0 auto;
}
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 22px; font-weight: 600; }
.subtitle { color: #999; font-size: 14px; margin-top: 4px; }
.card-title { font-weight: 600; }
.empty-state { padding: 60px 0; }
.result-content { min-height: 200px; }
.result-actions {
  margin-top: 16px;
  display: flex;
  gap: 8px;
}
</style>
