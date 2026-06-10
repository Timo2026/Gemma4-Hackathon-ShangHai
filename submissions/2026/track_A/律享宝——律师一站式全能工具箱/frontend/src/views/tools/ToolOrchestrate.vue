<template>
  <div class="tool-orchestrate">
    <div class="page-header">
      <h2>AI 工具智能编排</h2>
      <p class="subtitle">输入您的需求，AI 自动选择工具并编排执行流程</p>
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :md="14">
        <el-card shadow="never">
          <template #header><span class="card-title">🎯 输入需求</span></template>
          <el-form label-position="top" size="large">
            <el-form-item label="请描述您需要处理的法律事务">
              <el-input
                v-model="query"
                type="textarea"
                :rows="6"
                placeholder="例如：我收到一份民间借贷纠纷的起诉状，需要分析对方的诉讼请求是否合理，并起草一份答辩状..."
              />
            </el-form-item>
            <el-form-item label="选择工具（可选，不选则 AI 自动推荐）">
              <el-select v-model="selectedTools" multiple placeholder="自动推荐" style="width:100%">
                <el-option v-for="tool in allTools" :key="tool.id" :label="tool.name" :value="tool.id" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" size="large" @click="handleOrchestrate" style="width:100%">
                {{ loading ? 'AI 编排中...' : '🚀 开始智能编排' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="10">
        <el-card shadow="never">
          <template #header><span class="card-title">📋 执行流程</span></template>
          <div v-if="steps.length === 0" class="steps-empty">
            <el-empty description="输入需求后开始编排">
              <template #image>
                <el-icon :size="48" color="#c0c4cc"><Connection /></el-icon>
              </template>
            </el-empty>
          </div>
          <el-steps v-else direction="vertical" :active="currentStep" finish-status="success">
            <el-step v-for="(step, idx) in steps" :key="idx" :title="step.tool" :description="step.action">
              <template #icon>
                <el-icon v-if="step.status === 'completed'"><Check /></el-icon>
                <el-icon v-else-if="step.status === 'running'"><Loading /></el-icon>
                <el-icon v-else><MoreFilled /></el-icon>
              </template>
            </el-step>
          </el-steps>
        </el-card>
      </el-col>
    </el-row>

    <!-- 结果展示 -->
    <el-card v-if="result" shadow="never" class="result-card">
      <template #header>
        <div class="result-header">
          <span class="card-title">✅ 编排结果</span>
          <el-button size="small" @click="copyResult">复制结果</el-button>
        </div>
      </template>
      <div class="markdown-body" v-html="renderedResult"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToolStore } from '@/stores/tools'
import { marked } from 'marked'
import { ElMessage } from 'element-plus'

const route = useRoute()
const toolStore = useToolStore()

const query = ref('')
const selectedTools = ref([])
const loading = ref(false)
const steps = ref([])
const currentStep = ref(-1)
const result = ref(null)
const allTools = ref([])

const renderedResult = computed(() => {
  if (!result.value?.orchestration) return ''
  return marked(result.value.orchestration)
})

async function handleOrchestrate() {
  if (!query.value.trim()) {
    ElMessage.warning('请输入您的需求')
    return
  }

  loading.value = true
  steps.value = []
  currentStep.value = -1

  // 模拟编排步骤
  const toolNames = selectedTools.value.length > 0
    ? selectedTools.value
    : ['法律检索', '文书分析', '文书生成', '质量检查']

  for (let i = 0; i < toolNames.length; i++) {
    steps.value.push({ tool: toolNames[i], action: '处理中...', status: 'pending' })
  }

  try {
    // 逐步执行
    for (let i = 0; i < steps.value.length; i++) {
      currentStep.value = i
      steps.value[i].status = 'running'
      steps.value[i].action = `正在使用 ${steps.value[i].tool}...`
      await new Promise(r => setTimeout(r, 800))
      steps.value[i].status = 'completed'
      steps.value[i].action = `${steps.value[i].tool} 完成`
    }

    // 调用 API
    const res = await toolStore.orchestrate({
      query: query.value,
      tools: selectedTools.value,
    })
    result.value = res
    ElMessage.success('编排完成！')
  } catch (err) {
    // 错误已处理
  } finally {
    loading.value = false
  }
}

function copyResult() {
  if (!result.value?.orchestration) return
  navigator.clipboard.writeText(result.value.orchestration).then(() => {
    ElMessage.success('已复制')
  })
}

onMounted(() => {
  toolStore.fetchCatalog().then(catalog => {
    allTools.value = catalog.flatMap(g => g.items)
  })
  if (route.query.toolId) {
    selectedTools.value = [route.query.toolId]
  }
})
</script>

<style scoped>
.tool-orchestrate {
  max-width: 1200px;
  margin: 0 auto;
}
.page-header {
  margin-bottom: 24px;
}
.page-header h2 { font-size: 22px; font-weight: 600; }
.subtitle { color: #999; font-size: 14px; margin-top: 4px; }
.card-title { font-weight: 600; font-size: 15px; }
.steps-empty { padding: 60px 0; }
.result-card {
  margin-top: 20px;
  border-radius: 12px;
}
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
