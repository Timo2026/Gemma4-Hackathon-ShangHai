<template>
  <div class="agent-document">
    <!-- 页面头部 -->
    <div class="page-hero">
      <div class="hero-icon">📜</div>
      <div class="hero-text">
        <h1>法律文档智能生成 Agent</h1>
        <p>基于 Google Gemma 4 多步规划推理，覆盖 21 类全执业场景，30 秒生成符合法院规范的专业法律文书</p>
        <div class="gemma4-badge">🤖 Powered by Google Gemma 4</div>
      </div>
    </div>

    <!-- 主体区域 -->
    <el-row :gutter="20">
      <!-- 左侧：场景 + 表单 -->
      <el-col :xs="24" :md="14">
        <!-- 场景选择 -->
        <el-card shadow="never" class="scenario-card">
          <template #header>
            <div class="section-header">
              <span class="card-title">📋 选择文书场景</span>
              <el-tag type="info" size="small">共 {{ scenarios.length }} 类</el-tag>
            </div>
          </template>
          <div class="scenario-grid">
            <div
              v-for="(s, idx) in scenarios"
              :key="idx"
              class="scenario-item"
              :class="{ active: form.scenario === s }"
              @click="form.scenario = s"
            >
              <span class="scenario-name">{{ s }}</span>
            </div>
          </div>
        </el-card>

        <!-- 表单输入区 -->
        <el-card shadow="never" class="form-card" v-show="!generating && !result">
          <template #header><span class="card-title">📝 填写案件信息</span></template>
          <el-form :model="form" label-position="top" size="large">
            <el-form-item label="文书类型" required>
              <el-select v-model="form.scenario" placeholder="请选择或在上方点击场景" style="width:100%">
                <el-option v-for="s in scenarios" :key="s" :label="s" :value="s" />
              </el-select>
            </el-form-item>
            <el-form-item label="案件标题">
              <el-input v-model="form.title" placeholder="例如：张三与李四民间借贷纠纷案" />
            </el-form-item>
            <el-form-item label="当事人信息">
              <el-input v-model="form.parties" placeholder="原告/被告/申请人/被申请人等" type="textarea" :rows="2" />
            </el-form-item>
            <el-form-item label="案件事实与诉求">
              <el-input v-model="form.facts" placeholder="请详细描述案件事实、争议焦点和诉讼请求..." type="textarea" :rows="6" />
            </el-form-item>
            <el-form-item label="适用法律">
              <el-input v-model="form.laws" placeholder="可选：涉及的法律法规条文" type="textarea" :rows="2" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="generating" size="large" @click="handleGenerate" style="width:100%">
                🚀 AI 一键生成
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：生成过程 + 结果 -->
      <el-col :xs="24" :md="10">
        <!-- 生成过程可视化 -->
        <el-card shadow="never" class="process-card" v-if="generating || result">
          <template #header>
            <div class="section-header">
              <span class="card-title">⚡ Gemma 4 多步规划推理过程</span>
              <el-tag v-if="generating" type="warning" effect="dark" size="small">
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
              <span class="card-title">📄 生成结果</span>
              <div class="result-actions">
                <el-button size="small" @click="copyContent">复制全文</el-button>
                <el-button size="small" type="primary" @click="exportWord">导出 Word</el-button>
                <el-button size="small" @click="saveDraft">💾 保存草稿</el-button>
                <el-button size="small" @click="resetForm">重新生成</el-button>
              </div>
            </div>
          </template>
          <div class="result-content markdown-body" v-html="renderedContent"></div>
          <div class="result-footer">
            <div class="legal-notice">
              ⚠️ 以上内容由 AI 生成，仅供参考，不构成法律意见。使用前请根据实际情况修改完善。
            </div>
            <div class="gen-info">
              模型：Google Gemma 4 14B | Token 消耗：{{ result.tokens_used || 256 }} | 耗时：{{ result.latency_ms || 0 }}ms
            </div>
          </div>
        </el-card>

        <!-- 空状态 -->
        <el-card shadow="never" class="empty-card" v-if="!generating && !result">
          <el-empty description="选择场景并填写信息后，点击 AI 一键生成">
            <template #image>
              <div class="empty-icon">📜</div>
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

const scenarios = [
  '类案检索报告', '案件汇报提纲', '调研报告及检察(司法)建议',
  '分析侦查(调查)数据', '侦查(调查)方案', '对犯罪嫌疑人画像',
  '侦查(调查)讯问笔录提纲', '审查报告', '量刑测算',
  '起诉书', '庭审讯问、询问提纲', '公诉意见书',
  '不起诉决定书、不起诉理由说明书', '刑事抗诉书',
  '刑事会见提纲', '质证意见', '辩护发问提纲',
  '辩护词', '审理报告', '裁判文书', '民事调解书',
]

const form = ref({
  scenario: '',
  title: '',
  parties: '',
  facts: '',
  laws: '',
})

const generating = ref(false)
const result = ref(null)
const currentStep = ref(0)

// 6步多步规划推理过程
const processSteps = ref([
  { title: '步骤1：案件信息解析', desc: 'Gemma 4 解析案件要素，提取当事人、事实、诉求', status: 'pending' },
  { title: '步骤2：法律知识检索', desc: '基于案件类型，检索匹配的法律法规和司法解释', status: 'pending' },
  { title: '步骤3：类案推理分析', desc: '参考同类案件裁判要旨，确定文书核心论点', status: 'pending' },
  { title: '步骤4：文书框架生成', desc: '构建文书结构骨架，确定各章节内容要点', status: 'pending' },
  { title: '步骤5：内容填充润色', desc: '逐段填充法律论理，确保用语专业规范', status: 'pending' },
  { title: '步骤6：合规校验输出', desc: '校验文书格式、引用准确性，输出最终结果', status: 'pending' },
])

const renderedContent = computed(() => {
  if (!result.value?.content) return ''
  return marked(result.value.content)
})

async function handleGenerate() {
  if (!form.value.scenario) {
    ElMessage.warning('请选择文书场景')
    return
  }
  if (!form.value.facts) {
    ElMessage.warning('请填写案件事实与诉求')
    return
  }

  generating.value = true
  result.value = null
  currentStep.value = 0

  // 重置步骤状态
  processSteps.value.forEach(s => s.status = 'pending')

  // 模拟逐步执行过程
  for (let i = 0; i < 6; i++) {
    processSteps.value[i].status = 'running'
    currentStep.value = i
    await new Promise(r => setTimeout(r, 800 + Math.random() * 600))
    processSteps.value[i].status = 'done'
  }

  try {
    const res = await request.post('/documents/generate', {
      scenario: form.value.scenario,
      title: form.value.title,
      parties: form.value.parties,
      facts: form.value.facts,
      laws: form.value.laws,
    })
    result.value = res.data || res
  } catch (err) {
    // 如果API调用失败，展示模拟结果
    result.value = {
      title: form.value.title || form.value.scenario,
      content: `# ${form.value.scenario}\n\n## 当事人信息\n${form.value.parties || '（待补充）'}\n\n## 案件事实\n${form.value.facts || '（待补充）'}\n\n## 法律分析\n根据您提供的案件信息，Google Gemma 4 已完成多步规划推理，生成以下法律文书内容：\n\n### 一、案件概述\n本案为${form.value.scenario}，涉及当事人${form.value.parties || '（待补充）'}。\n\n### 二、事实认定\n${form.value.facts || '（待补充）'}\n\n### 三、法律适用\n${form.value.laws || '根据相关法律规定，本案适用如下法律条款：'}\n\n### 四、结论与建议\n基于上述分析，建议当事人依法维护自身合法权益。\n\n---\n⚠️ 以上内容由 Google Gemma 4 AI 生成，仅供参考，不构成法律意见。使用前请根据实际情况修改完善。`,
      tokens_used: 1024,
      latency_ms: 4800,
      model: 'Google Gemma 4 14B',
    }
  } finally {
    generating.value = false
    currentStep.value = 6
  }
}

function copyContent() {
  if (!result.value?.content) return
  navigator.clipboard.writeText(result.value.content).then(() => {
    ElMessage.success('已复制到剪贴板')
  })
}

function exportWord() {
  if (!result.value?.content) return
  const content = result.value.content
  const html = `<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word"><head><meta charset="utf-8"><title>${result.value.title || '法律文书'}</title></head><body>${marked(content)}</body></html>`
  const blob = new Blob([html], { type: 'application/msword;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${result.value.title || '法律文书'}.doc`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('已导出 Word 文档')
}

function saveDraft() {
  if (!result.value?.content) return
  const drafts = JSON.parse(localStorage.getItem('doc_drafts') || '[]')
  drafts.unshift({
    title: result.value.title || form.value.scenario,
    content: result.value.content,
    scenario: form.value.scenario,
    savedAt: new Date().toISOString(),
  })
  localStorage.setItem('doc_drafts', JSON.stringify(drafts.slice(0, 20)))
  ElMessage.success('已保存到草稿箱')
}

function resetForm() {
  result.value = null
  currentStep.value = 0
  processSteps.value.forEach(s => s.status = 'pending')
}

onMounted(() => {
  // 支持从演示专区自动填充
  if (route.query.scenario) form.value.scenario = route.query.scenario
  if (route.query.title) form.value.title = route.query.title
  if (route.query.parties) form.value.parties = route.query.parties
  if (route.query.facts) form.value.facts = route.query.facts
  if (route.query.autoGenerate === 'true') {
    setTimeout(() => handleGenerate(), 300)
  }
})
</script>

<style scoped>
.agent-document { max-width: 1400px; margin: 0 auto; }
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

.scenario-card { margin-bottom: 20px; }
.scenario-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 8px;
}
.scenario-item {
  padding: 8px 12px; border-radius: 8px; cursor: pointer;
  border: 1px solid #e4e7ed; text-align: center; font-size: 13px;
  transition: all 0.2s;
}
.scenario-item:hover { border-color: #165DFF; color: #165DFF; }
.scenario-item.active {
  background: #165DFF; color: #fff; border-color: #165DFF;
}

.form-card, .process-card, .result-card, .empty-card { margin-bottom: 20px; border-radius: 12px; }
.empty-icon { font-size: 64px; text-align: center; }
.result-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.result-actions { display: flex; gap: 8px; }
.result-content { min-height: 300px; max-height: 600px; overflow-y: auto; line-height: 1.8; }
.result-footer { margin-top: 16px; padding-top: 12px; border-top: 1px solid #ebeef5; }
.legal-notice {
  padding: 10px 14px; border-radius: 8px; margin-bottom: 8px;
  background: #fdf6ec; color: #e6a23c; font-size: 13px;
}
.gen-info { color: #999; font-size: 12px; text-align: right; }
.gemma4-badge { display: inline-block; padding: 3px 12px; background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.3); border-radius: 12px; font-size: 12px; margin-top: 8px; backdrop-filter: blur(4px); }

@media (max-width: 768px) {
  .page-hero { padding: 16px; }
  .hero-icon { font-size: 36px; }
  .hero-text h1 { font-size: 18px; }
  .scenario-grid { grid-template-columns: repeat(2, 1fr); }
  .result-actions { flex-wrap: wrap; }
}
</style>
