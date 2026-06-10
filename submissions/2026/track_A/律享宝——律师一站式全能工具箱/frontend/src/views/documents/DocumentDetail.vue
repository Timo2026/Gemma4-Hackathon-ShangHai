<template>
  <div class="doc-detail">
    <div class="page-header">
      <el-button text @click="$router.push('/documents')">
        <el-icon><ArrowLeft /></el-icon> 返回列表
      </el-button>
    </div>

    <el-card shadow="never" v-loading="loading">
      <template #header>
        <div class="detail-header">
          <div>
            <h2>{{ doc?.title || '文书详情' }}</h2>
            <el-tag :type="doc?.status === 'completed' ? 'success' : 'warning'" size="small">
              {{ doc?.status === 'completed' ? '已完成' : '生成中' }}
            </el-tag>
          </div>
          <div class="detail-actions">
            <el-button size="small" @click="copyContent">复制</el-button>
            <el-button size="small" type="primary" @click="exportDoc">导出</el-button>
          </div>
        </div>
      </template>
      <div v-if="doc?.content" class="markdown-body" v-html="renderedContent"></div>
      <el-empty v-else description="暂无内容" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useDocumentStore } from '@/stores/documents'
import { marked } from 'marked'
import { ElMessage } from 'element-plus'

const route = useRoute()
const docStore = useDocumentStore()
const loading = ref(false)
const doc = ref(null)

const renderedContent = computed(() => {
  if (!doc.value?.content) return ''
  return marked(doc.value.content)
})

function copyContent() {
  if (!doc.value?.content) return
  navigator.clipboard.writeText(doc.value.content).then(() => {
    ElMessage.success('已复制')
  })
}

function exportDoc() {
  if (!doc.value?.content) return
  const blob = new Blob([doc.value.content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${doc.value.title || '文书'}.md`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  loading.value = true
  try {
    const id = route.params.id
    if (id) {
      doc.value = await docStore.getDetail(id)
    }
  } catch (err) {
    // 错误已处理
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.doc-detail {
  max-width: 900px;
  margin: 0 auto;
}
.page-header {
  margin-bottom: 16px;
}
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}
.detail-header h2 {
  font-size: 18px;
  margin-bottom: 8px;
}
.detail-actions {
  display: flex;
  gap: 8px;
}
</style>
