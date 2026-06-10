<template>
  <div class="generate-doc">
    <div class="page-header">
      <h2>AI 智能生成法律文书</h2>
      <p class="subtitle">基于 Gemma 4 大模型，一键生成专业法律文书</p>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：填写表单 -->
      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <template #header><span class="card-title">📝 填写案件信息</span></template>
          <el-form :model="form" label-position="top" size="large">
            <el-form-item label="文书类型" required>
              <el-select v-model="form.scenario" placeholder="请选择文书类型" style="width:100%" @change="onScenarioChange">
                <el-option-group
                  v-for="group in docStore.scenarios"
                  :key="group.category"
                  :label="group.category"
                >
                  <el-option v-for="item in group.items" :key="item.id" :label="item.name" :value="item.id">
                    <span>{{ item.name }}</span>
                    <span class="option-desc">{{ item.desc }}</span>
                  </el-option>
                </el-option-group>
              </el-select>
            </el-form-item>
            <el-form-item label="案件标题">
              <el-input v-model="form.title" placeholder="例如：张三与李四合同纠纷案" />
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
                {{ generating ? 'AI 正在生成中...' : '🚀 AI 生成文书' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：文书预览 -->
      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <template #header>
            <div class="preview-header">
              <span class="card-title">📄 文书预览</span>
              <div v-if="result" class="preview-actions">
                <el-button size="small" @click="copyContent">复制</el-button>
                <el-button size="small" type="primary" @click="exportDoc">导出</el-button>
              </div>
            </div>
          </template>
          <div v-if="!result && !generating" class="preview-empty">
            <el-empty description="填写左侧信息后，点击生成">
              <template #image>
                <el-icon :size="60" color="#c0c4cc"><Document /></el-icon>
              </template>
            </el-empty>
          </div>
          <div v-loading="generating" class="preview-content">
            <div v-if="result" class="markdown-body" v-html="renderedContent"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useDocumentStore } from '@/stores/documents'
import { marked } from 'marked'
import { ElMessage } from 'element-plus'

const docStore = useDocumentStore()
const generating = ref(false)
const result = ref(null)

const form = reactive({
  scenario: '',
  title: '',
  parties: '',
  facts: '',
  laws: '',
})

const renderedContent = computed(() => {
  if (!result?.content) return ''
  return marked(result.content)
})

function onScenarioChange(val) {
  const allItems = docStore.scenarios.flatMap(g => g.items)
  const selected = allItems.find(i => i.id === val)
  if (selected && selected.default_template) {
    form.title = form.title || selected.default_template.title || ''
    form.parties = form.parties || selected.default_template.parties || ''
    form.facts = form.facts || selected.default_template.facts || ''
  }
}

async function handleGenerate() {
  if (!form.scenario) {
    ElMessage.warning('请选择文书类型')
    return
  }
  if (!form.facts) {
    ElMessage.warning('请填写案件事实')
    return
  }

  generating.value = true
  try {
    const res = await docStore.generate({
      scenario: form.scenario,
      title: form.title,
      parties: form.parties,
      facts: form.facts,
      laws: form.laws,
    })
    result.value = res
    ElMessage.success('文书生成成功！')
  } catch (err) {
    // 错误已处理
  } finally {
    generating.value = false
  }
}

function copyContent() {
  if (!result?.content) return
  navigator.clipboard.writeText(result.content).then(() => {
    ElMessage.success('已复制到剪贴板')
  })
}

function exportDoc() {
  if (!result?.content) return
  const blob = new Blob([result.content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${result.title || '文书'}.md`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(() => {
  docStore.fetchScenarios()
})
</script>

<style scoped>
.generate-doc {
  max-width: 1400px;
  margin: 0 auto;
}
.page-header {
  margin-bottom: 24px;
}
.page-header h2 {
  font-size: 22px;
  font-weight: 600;
}
.subtitle {
  color: #999;
  font-size: 14px;
  margin-top: 4px;
}
.card-title {
  font-weight: 600;
  font-size: 15px;
}
.option-desc {
  float: right;
  color: #999;
  font-size: 12px;
}
.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.preview-empty {
  padding: 80px 0;
}
.preview-content {
  min-height: 400px;
  max-height: 600px;
  overflow-y: auto;
}
</style>
