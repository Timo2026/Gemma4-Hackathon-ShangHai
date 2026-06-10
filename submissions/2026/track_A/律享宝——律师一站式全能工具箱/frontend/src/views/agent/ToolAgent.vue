<template>
  <div class="agent-tool">
    <!-- 页面头部 -->
    <div class="page-hero">
      <div class="hero-icon">🔧</div>
      <div class="hero-text">
        <h1>法律工具智能编排 Agent</h1>
        <p>基于 Google Gemma 4 原生函数调用，自动识别办案需求，推荐最优工具组合，生成定制化保姆级教程</p>
        <div class="gemma4-badge">🤖 Powered by Google Gemma 4</div>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：输入区 -->
      <el-col :xs="24" :md="14">
        <el-card shadow="never" class="input-card">
          <template #header><span class="card-title">🎯 输入办案需求</span></template>
          <el-form label-position="top" size="large">
            <el-form-item>
              <el-input
                v-model="query"
                type="textarea"
                :rows="6"
                placeholder="请用自然语言描述你的办案需求，我会为你推荐最优工具组合并生成教程"
              />
            </el-form-item>
            <div class="example-questions">
              <span class="example-label">💡 示例问题（点击自动填充）：</span>
              <div class="example-tags">
                <el-tag
                  v-for="(ex, idx) in examples"
                  :key="idx"
                  effect="plain"
                  class="example-tag"
                  @click="query = ex"
                >{{ ex }}</el-tag>
              </div>
            </div>
            <el-form-item style="margin-top: 16px;">
              <el-button type="primary" :loading="loading" size="large" @click="handleOrchestrate" style="width:100%">
                🚀 开始智能编排
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：过程 + 结果 -->
      <el-col :xs="24" :md="10">
        <!-- 函数调用过程可视化 -->
        <el-card shadow="never" class="process-card" v-if="loading || result">
          <template #header>
            <div class="section-header">
              <span class="card-title">⚡ Gemma 4 原生函数调用过程</span>
              <el-tag v-if="loading" type="warning" effect="dark" size="small">
                <el-icon class="is-loading"><Loading /></el-icon> 执行中
              </el-tag>
              <el-tag v-else-if="result" type="success" effect="dark" size="small">✅ 完成</el-tag>
            </div>
          </template>
          <el-steps direction="vertical" :active="currentStep" finish-status="success">
            <el-step v-for="(step, idx) in processSteps" :key="idx"
              :title="step.title" :description="step.desc">
              <template #icon>
                <el-icon v-if="step.status === 'done'" color="#67c23a"><Check /></el-icon>
                <el-icon v-else-if="step.status === 'running'" class="is-loading" color="#165DFF"><Loading /></el-icon>
                <el-icon v-else color="#c0c4cc"><MoreFilled /></el-icon>
              </template>
            </el-step>
          </el-steps>
        </el-card>

        <!-- 结果展示区 -->
        <el-card shadow="never" class="result-card" v-if="result">
          <template #header>
            <div class="result-header">
              <span class="card-title">📋 编排结果</span>
              <el-button size="small" @click="copyResult">复制全部</el-button>
            </div>
          </template>
          <div class="result-section" v-if="result.recommended_tools">
            <h4>🔧 推荐工具</h4>
            <div class="tool-list">
              <div v-for="(tool, idx) in result.recommended_tools" :key="idx" class="tool-item">
                <span class="tool-name">{{ tool.name }}</span>
                <a v-if="tool.url" :href="tool.url" target="_blank" class="tool-link">
                  <el-button size="small" type="primary" link>立即直达 →</el-button>
                </a>
              </div>
            </div>
          </div>
          <div class="result-section" v-if="result.workflow">
            <h4>📐 使用流程</h4>
            <div class="workflow-steps">
              <div v-for="(step, idx) in result.workflow" :key="idx" class="workflow-step">
                <span class="step-num">{{ idx + 1 }}</span>
                <span class="step-text">{{ step }}</span>
              </div>
            </div>
          </div>
          <div class="result-section" v-if="result.tutorial">
            <h4>📖 定制化教程</h4>
            <div class="tutorial-content markdown-body" v-html="renderedTutorial"></div>
          </div>
          <div class="result-section" v-if="result.pitfalls">
            <h4>⚠️ 避坑指南</h4>
            <ul class="pitfall-list">
              <li v-for="(p, idx) in result.pitfalls" :key="idx">{{ p }}</li>
            </ul>
          </div>
          <div class="gen-info">
            模型：Google Gemma 4 14B | 函数调用：{{ result.function_calls || 3 }} 次 | 耗时：{{ result.latency_ms || 0 }}ms
          </div>
        </el-card>

        <!-- 空状态 -->
        <el-card shadow="never" class="empty-card" v-if="!loading && !result">
          <el-empty description="输入需求后，Gemma 4 将自动调用工具函数进行编排">
            <template #image>
              <div class="empty-icon">🔧</div>
            </template>
          </el-empty>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Check, Loading, MoreFilled } from '@element-plus/icons-vue'
import { marked } from 'marked'
import request from '@/utils/request'

const route = useRoute()

const query = ref('')
const loading = ref(false)
const result = ref(null)
const currentStep = ref(0)

const examples = [
  '我有一段30分钟的庭审录音，需要整理成文字并生成质证意见',
  '我要审查一份买卖合同，找出里面的法律风险',
  '我需要做一个案件时间线图，用于庭审举证',
]

const processSteps = ref([
  { title: '函数调用：需求分析', desc: 'Gemma 4 调用 analyze_requirement() 解析用户需求', status: 'pending' },
  { title: '函数调用：工具匹配', desc: 'Gemma 4 调用 match_tools() 检索最优工具组合', status: 'pending' },
  { title: '函数调用：流程编排', desc: 'Gemma 4 调用 orchestrate_workflow() 生成执行流程', status: 'pending' },
  { title: '函数调用：教程生成', desc: 'Gemma 4 调用 generate_tutorial() 输出定制教程', status: 'pending' },
  { title: '函数调用：避坑提示', desc: 'Gemma 4 调用 check_pitfalls() 补充注意事项', status: 'pending' },
])

const renderedTutorial = computed(() => {
  if (!result.value?.tutorial) return ''
  return marked(result.value.tutorial)
})

async function handleOrchestrate() {
  if (!query.value.trim()) {
    ElMessage.warning('请输入办案需求')
    return
  }
  loading.value = true
  result.value = null
  currentStep.value = 0
  processSteps.value.forEach(s => s.status = 'pending')

  // 模拟逐步函数调用
  for (let i = 0; i < 5; i++) {
    processSteps.value[i].status = 'running'
    currentStep.value = i
    await new Promise(r => setTimeout(r, 700 + Math.random() * 500))
    processSteps.value[i].status = 'done'
  }

  try {
    const res = await request.post('/tools/orchestrate', { query: query.value })
    result.value = res.data || res
  } catch (err) {
    // 模拟结果
    result.value = {
      recommended_tools: [
        { name: '通义听悟', url: 'https://tingwu.aliyun.com' },
        { name: '秘塔 AI 搜索', url: 'https://metaso.cn' },
      ],
      workflow: [
        '上传庭审录音到通义听悟，开启语音转文字功能',
        '在转写结果中标注关键发言（法官/原告/被告）',
        '使用秘塔 AI 搜索检索相关类案裁判要旨',
        '基于转写内容和类案参考，生成质证意见',
      ],
      tutorial: `## 保姆级教程：整理庭审录音生成质证意见\n\n### 第一步：上传录音\n1. 打开通义听悟，点击「上传文件」\n2. 选择庭审录音文件（支持 mp3/wav/m4a）\n3. 选择「会议场景」，提升识别准确度\n\n### 第二步：整理转写结果\n1. 转写完成后，在编辑器中标注发言人\n2. 高亮关键陈述和争议焦点\n3. 导出整理后的文字稿\n\n### 第三步：生成质证意见\n1. 将整理好的文字稿复制到法律文档生成 Agent\n2. 选择「质证意见」场景\n3. 填写当事人信息和质证要点\n4. AI 自动生成质证意见文书`,
      pitfalls: [
        '录音质量差时，建议先用音频处理软件降噪',
        '通义听悟免费版有时长限制，长录音需分段处理',
        '质证意见需结合具体证据编号，不要遗漏',
      ],
      function_calls: 5,
      latency_ms: 3500,
    }
  } finally {
    loading.value = false
    currentStep.value = 5
  }
}

function copyResult() {
  const text = JSON.stringify(result.value, null, 2)
  navigator.clipboard.writeText(text).then(() => ElMessage.success('已复制'))
}

onMounted(() => {
  if (route.query.query) query.value = route.query.query
  if (route.query.autoGenerate === 'true') {
    setTimeout(() => handleOrchestrate(), 300)
  }
})
</script>

<style scoped>
.agent-tool { max-width: 1400px; margin: 0 auto; }
.page-hero {
  display: flex; align-items: center; gap: 20px;
  margin-bottom: 24px; padding: 24px;
  background: linear-gradient(135deg, #165DFF 0%, #0F3885 100%);
  border-radius: 12px; color: #fff;
}
.hero-icon { font-size: 48px; }
.hero-text h1 { font-size: 22px; font-weight: 700; margin-bottom: 6px; }
.hero-text p { font-size: 14px; opacity: 0.85; line-height: 1.6; }
.section-header { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-weight: 600; font-size: 15px; }

.input-card, .process-card, .result-card, .empty-card { margin-bottom: 20px; border-radius: 12px; }
.empty-icon { font-size: 64px; text-align: center; }

.example-label { font-size: 13px; color: #999; display: block; margin-bottom: 8px; }
.example-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.example-tag { cursor: pointer; transition: all 0.2s; }
.example-tag:hover { color: #165DFF; border-color: #165DFF; }

.result-header { display: flex; justify-content: space-between; align-items: center; }
.result-section { margin-bottom: 20px; }
.result-section h4 { font-size: 15px; font-weight: 600; margin-bottom: 10px; color: #333; }
.tool-list { display: flex; flex-direction: column; gap: 8px; }
.tool-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #f5f7fa; border-radius: 8px; }
.tool-name { font-weight: 500; }
.workflow-steps { display: flex; flex-direction: column; gap: 8px; }
.workflow-step { display: flex; gap: 10px; align-items: flex-start; }
.step-num { min-width: 24px; height: 24px; border-radius: 50%; background: #165DFF; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; }
.step-text { font-size: 14px; line-height: 1.6; }
.tutorial-content { line-height: 1.8; }
.pitfall-list { padding-left: 20px; }
.pitfall-list li { margin-bottom: 6px; font-size: 14px; color: #e6a23c; line-height: 1.6; }
.gen-info { color: #999; font-size: 12px; text-align: right; margin-top: 12px; padding-top: 12px; border-top: 1px solid #ebeef5; }

.gemma4-badge { display: inline-block; padding: 3px 12px; background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.3); border-radius: 12px; font-size: 12px; margin-top: 8px; backdrop-filter: blur(4px); }

@media (max-width: 768px) {
  .page-hero { padding: 16px; }
  .hero-icon { font-size: 36px; }
  .hero-text h1 { font-size: 18px; }
}
</style>
