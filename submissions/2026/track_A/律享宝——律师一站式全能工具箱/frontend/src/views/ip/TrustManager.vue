<template>
  <div class="trust-manager">
    <div class="page-header">
      <div>
        <h2>信任背书</h2>
        <p class="subtitle">展示资质证书、荣誉奖项，AI 生成信任建设内容</p>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <template #header><span class="card-title">📜 信任背书类型</span></template>
          <div v-if="trustTypes.length === 0" class="empty-state">
            <el-empty :image-size="80" description="暂无信任背书类型数据" />
          </div>
          <div v-else>
            <el-tag
              v-for="t in trustTypes"
              :key="t"
              style="margin: 4px"
              size="large"
              effect="plain"
            >
              {{ t }}
            </el-tag>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <template #header><span class="card-title">✨ AI 生成信任内容</span></template>
          <el-form :model="form" label-position="top">
            <el-form-item label="选择信任背书类型">
              <el-select v-model="form.type" style="width:100%">
                <el-option label="执业资质展示" value="执业资质" />
                <el-option label="荣誉奖项" value="荣誉奖项" />
                <el-option label="媒体报道" value="媒体报道" />
                <el-option label="客户评价" value="客户评价" />
                <el-option label="学术成果" value="学术成果" />
              </el-select>
            </el-form-item>
            <el-form-item label="描述您的背景">
              <el-input v-model="form.description" type="textarea" :rows="4" placeholder="例如：执业15年，获评市级优秀律师，代理案件入选最高院典型案例..." />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="handleGenerate" style="width:100%">
                {{ loading ? 'AI 生成中...' : '🚀 生成信任背书内容' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <!-- 生成结果 -->
    <el-card v-if="result" shadow="never" class="result-card">
      <template #header>
        <div class="result-header">
          <span class="card-title">✅ 生成结果</span>
          <el-button size="small" @click="copyResult">复制</el-button>
        </div>
      </template>
      <div class="markdown-body" v-html="renderedResult"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useIPStore } from '@/stores/ip'
import { marked } from 'marked'
import { ElMessage } from 'element-plus'

const ipStore = useIPStore()
const loading = ref(false)
const result = ref(null)
const trustTypes = ref([])

const form = reactive({
  type: '执业资质',
  description: '',
})

const renderedResult = computed(() => {
  if (!result?.content) return ''
  return marked(result.content)
})

async function handleGenerate() {
  if (!form.description) {
    ElMessage.warning('请描述您的背景信息')
    return
  }
  loading.value = true
  try {
    const res = await ipStore.generateTrustContent({ ...form })
    result.value = res
    ElMessage.success('信任背书内容生成成功！')
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

onMounted(async () => {
  try {
    trustTypes.value = await ipStore.fetchTrustTypes()
  } catch (e) {
    trustTypes.value = ['执业资质', '荣誉奖项', '媒体报道', '客户评价', '学术成果']
  }
})
</script>

<style scoped>
.trust-manager {
  max-width: 1200px;
  margin: 0 auto;
}
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 22px; font-weight: 600; }
.subtitle { color: #999; font-size: 14px; margin-top: 4px; }
.card-title { font-weight: 600; }
.empty-state { padding: 40px 0; }
.result-card { margin-top: 20px; border-radius: 12px; }
.result-header { display: flex; justify-content: space-between; align-items: center; }
</style>
