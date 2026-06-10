<template>
  <div class="template-fill">
    <div class="page-header">
      <el-button text @click="$router.push('/templates')">
        <el-icon><ArrowLeft /></el-icon> 返回模板库
      </el-button>
      <h2>{{ template?.name || '填写文书' }}</h2>
      <el-tag v-if="template?.source" size="small" type="info">{{ template.source }}</el-tag>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：表单 -->
      <el-col :xs="24" :md="14">
        <el-card shadow="never" v-loading="tplStore.loading">
          <template #header>
            <span class="card-title">📝 填写文书内容</span>
          </template>
          <el-form
            v-if="template"
            :model="formData"
            label-position="top"
            size="large"
            ref="formRef"
          >
            <template v-for="field in template.fields" :key="field.name">
              <!-- 文本 -->
              <el-form-item
                v-if="field.type === 'text'"
                :label="field.label"
                :required="field.required"
              >
                <el-input
                  v-model="formData[field.name]"
                  :placeholder="field.placeholder || `请输入${field.label}`"
                />
              </el-form-item>

              <!-- 日期 -->
              <el-form-item
                v-else-if="field.type === 'date'"
                :label="field.label"
                :required="field.required"
              >
                <el-date-picker
                  v-model="formData[field.name]"
                  type="date"
                  :placeholder="`请选择${field.label}`"
                  format="YYYY年MM月DD日"
                  value-format="YYYY年MM月DD日"
                  style="width:100%"
                />
              </el-form-item>

              <!-- 下拉选择 -->
              <el-form-item
                v-else-if="field.type === 'select'"
                :label="field.label"
                :required="field.required"
              >
                <el-select v-model="formData[field.name]" :placeholder="`请选择${field.label}`" style="width:100%">
                  <el-option v-for="opt in field.options" :key="opt.value" :label="opt.label" :value="opt.value" />
                </el-select>
              </el-form-item>

              <!-- 单选 -->
              <el-form-item
                v-else-if="field.type === 'radio'"
                :label="field.label"
                :required="field.required"
              >
                <el-radio-group v-model="formData[field.name]">
                  <el-radio v-for="opt in field.options" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </el-radio>
                </el-radio-group>
              </el-form-item>

              <!-- 多选 -->
              <el-form-item
                v-else-if="field.type === 'checkbox'"
                :label="field.label"
                :required="field.required"
              >
                <el-checkbox-group v-model="formData[field.name]">
                  <el-checkbox v-for="opt in field.options" :key="opt.value" :label="opt.value">
                    {{ opt.label }}
                  </el-checkbox>
                </el-checkbox-group>
              </el-form-item>

              <!-- 多行文本 -->
              <el-form-item
                v-else-if="field.type === 'textarea'"
                :label="field.label"
                :required="field.required"
              >
                <el-input
                  v-model="formData[field.name]"
                  type="textarea"
                  :rows="4"
                  :placeholder="field.placeholder || `请输入${field.label}`"
                />
              </el-form-item>

              <!-- 对象类型 -->
              <el-card
                v-else-if="field.type === 'object'"
                shadow="never"
                class="object-card"
              >
                <template #header>
                  <span class="object-title">{{ field.label }}</span>
                </template>
                <el-form-item
                  v-for="prop in field.properties"
                  :key="prop.name"
                  :label="prop.label"
                  :required="prop.required"
                >
                  <template v-if="prop.type === 'select'">
                    <el-select
                      :model-value="formData[field.name]?.[prop.name] || ''"
                      @update:model-value="setObjectField(field.name, prop.name, $event)"
                      :placeholder="`请选择`"
                      style="width:100%"
                    >
                      <el-option v-for="opt in prop.options" :key="opt.value" :label="opt.label" :value="opt.value" />
                    </el-select>
                  </template>
                  <template v-else-if="prop.type === 'date'">
                    <el-date-picker
                      :model-value="formData[field.name]?.[prop.name] || ''"
                      @update:model-value="setObjectField(field.name, prop.name, $event)"
                      type="date"
                      format="YYYY年MM月DD日"
                      value-format="YYYY年MM月DD日"
                      style="width:100%"
                    />
                  </template>
                  <template v-else>
                    <el-input
                      :model-value="formData[field.name]?.[prop.name] || ''"
                      @update:model-value="setObjectField(field.name, prop.name, $event)"
                      :placeholder="`请输入${prop.label}`"
                    />
                  </template>
                </el-form-item>
              </el-card>

              <!-- 数组类型 -->
              <el-card
                v-else-if="field.type === 'array'"
                shadow="never"
                class="array-card"
              >
                <template #header>
                  <div class="array-header">
                    <span class="object-title">{{ field.label }}</span>
                    <el-button size="small" type="primary" @click="addArrayItem(field.name, field.item)">
                      <el-icon><Plus /></el-icon> 添加
                    </el-button>
                  </div>
                </template>
                <div v-for="(item, idx) in (formData[field.name] || [])" :key="idx" class="array-item">
                  <div class="array-item-header">
                    <span>第{{ idx + 1 }}项</span>
                    <el-button size="small" type="danger" text @click="removeArrayItem(field.name, idx)">
                      <el-icon><Delete /></el-icon> 删除
                    </el-button>
                  </div>
                  <!-- 数组项为对象 -->
                  <template v-if="field.item?.type === 'object'">
                    <el-form-item
                      v-for="prop in field.item.properties"
                      :key="prop.name"
                      :label="prop.label"
                      :required="prop.required"
                    >
                      <el-input v-model="item[prop.name]" :placeholder="`请输入${prop.label}`" />
                    </el-form-item>
                  </template>
                  <!-- 数组项为文本 -->
                  <template v-else>
                    <el-input v-model="formData[field.name][idx]" :placeholder="`请输入${field.label}`" type="textarea" :rows="2" />
                  </template>
                </div>
                <el-empty v-if="!formData[field.name]?.length" :image-size="40" description="暂未添加" />
              </el-card>
            </template>

            <!-- 生成按钮 -->
            <el-form-item class="submit-row">
              <el-button type="primary" :loading="rendering" size="large" @click="handleRender" style="width:100%">
                {{ rendering ? '生成中...' : '🚀 生成文书' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：预览 -->
      <el-col :xs="24" :md="10">
        <el-card shadow="never" class="preview-card">
          <template #header>
            <div class="preview-header">
              <span class="card-title">📄 文书预览</span>
              <div v-if="renderResult" class="preview-actions">
                <el-button size="small" @click="copyContent">复制</el-button>
                <el-button size="small" type="primary" @click="exportDoc">导出Word</el-button>
              </div>
            </div>
          </template>
          <div v-if="!renderResult && !rendering" class="preview-empty">
            <el-empty description="填写左侧表单后点击生成" />
          </div>
          <div v-loading="rendering" class="preview-content">
            <div v-if="renderResult" class="rendered-doc" v-html="renderResult.html"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTemplateStore } from '@/stores/templates'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const tplStore = useTemplateStore()

const template = ref(null)
const formData = reactive({})
const renderResult = ref(null)
const rendering = ref(false)
const formRef = ref(null)

function getObjectField(fieldName, propName) {
  if (!formData[fieldName]) formData[fieldName] = {}
  return formData[fieldName][propName] || ''
}

function setObjectField(fieldName, propName, value) {
  if (!formData[fieldName]) formData[fieldName] = {}
  formData[fieldName][propName] = value
}

function addArrayItem(fieldName, itemDef) {
  if (!formData[fieldName]) formData[fieldName] = []
  if (itemDef?.type === 'object') {
    const newItem = {}
    itemDef.properties?.forEach(p => { newItem[p.name] = '' })
    formData[fieldName].push(newItem)
  } else {
    formData[fieldName].push('')
  }
}

function removeArrayItem(fieldName, idx) {
  formData[fieldName].splice(idx, 1)
}

async function handleRender() {
  if (!template.value) return
  rendering.value = true
  try {
    const result = await tplStore.renderTemplate(template.value.id, { ...formData })
    if (result) {
      renderResult.value = result
      ElMessage.success('文书生成成功！')
    }
  } catch (err) {
    ElMessage.error('生成失败')
  } finally {
    rendering.value = false
  }
}

function copyContent() {
  if (!renderResult.value?.content) return
  navigator.clipboard.writeText(renderResult.value.content).then(() => {
    ElMessage.success('已复制到剪贴板')
  })
}

function exportDoc() {
  if (!renderResult.value) return
  // 导出为HTML文件（可用Word打开）
  const html = renderResult.value.html
  const blob = new Blob([html], { type: 'application/msword;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${renderResult.value.title || '文书'}.doc`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  const templateId = route.params.id
  if (templateId) {
    const detail = await tplStore.fetchTemplateDetail(templateId)
    if (detail) {
      template.value = detail
      // 初始化表单默认值
      detail.fields?.forEach(field => {
        if (field.type === 'object') {
          formData[field.name] = {}
          field.properties?.forEach(p => { formData[field.name][p.name] = '' })
        } else if (field.type === 'array') {
          formData[field.name] = []
        } else if (field.type === 'checkbox') {
          formData[field.name] = []
        } else if (field.type === 'radio') {
          formData[field.name] = field.options?.[0]?.value ?? ''
        } else {
          formData[field.name] = ''
        }
      })
      // 预填案由默认值
      if (detail.case_cause_default) {
        const causeField = detail.fields?.find(f => f.name === 'case_cause')
        if (causeField) formData.case_cause = detail.case_cause_default
      }
    }
  }
})
</script>

<style scoped>
.template-fill {
  max-width: 1400px;
  margin: 0 auto;
}
.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.page-header h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}
.card-title {
  font-weight: 600;
  font-size: 15px;
}
.object-card {
  margin-bottom: 16px;
  border-radius: 8px;
}
.object-card :deep(.el-card__header) {
  padding: 12px 16px;
  background: #f5f7fa;
}
.object-title {
  font-weight: 600;
  font-size: 14px;
}
.array-card {
  margin-bottom: 16px;
  border-radius: 8px;
}
.array-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.array-item {
  padding: 12px;
  margin-bottom: 8px;
  background: #fafafa;
  border-radius: 6px;
}
.array-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
  color: #666;
}
.submit-row {
  margin-top: 24px;
}
.preview-card {
  position: sticky;
  top: 20px;
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
  max-height: 700px;
  overflow-y: auto;
}
.rendered-doc {
  font-family: "SimSun", serif;
  font-size: 14px;
  line-height: 2;
}
.rendered-doc :deep(.title) {
  font-size: 22px;
  font-weight: bold;
  text-align: center;
  letter-spacing: 4px;
  margin-bottom: 24px;
}
.rendered-doc :deep(.section-title) {
  font-size: 16px;
  font-weight: bold;
  margin-top: 16px;
  margin-bottom: 8px;
}
.rendered-doc :deep(.content) {
  text-indent: 2em;
  margin-bottom: 8px;
}
.rendered-doc :deep(.signature) {
  text-align: right;
  margin-top: 48px;
  line-height: 2;
}
.rendered-doc :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}
.rendered-doc :deep(td),
.rendered-doc :deep(th) {
  border: 1px solid #000;
  padding: 8px 12px;
  text-align: left;
}
.rendered-doc :deep(th) {
  background-color: #f5f5f5;
  font-weight: bold;
  width: 25%;
}
</style>
