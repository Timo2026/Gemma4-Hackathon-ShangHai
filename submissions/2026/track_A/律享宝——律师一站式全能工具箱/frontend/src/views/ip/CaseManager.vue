<template>
  <div class="case-manager">
    <div class="page-header">
      <div>
        <h2>案例管理</h2>
        <p class="subtitle">AI 将您的经典案例包装为可传播的专业内容</p>
      </div>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon> 添加案例
      </el-button>
    </div>

    <el-card shadow="never">
      <div class="empty-state">
        <el-empty description="暂无案例，点击「添加案例」开始创建">
          <el-button type="primary" @click="showAddDialog = true">添加案例</el-button>
        </el-empty>
      </div>
    </el-card>

    <!-- 添加案例对话框 -->
    <el-dialog v-model="showAddDialog" title="添加案例" width="600px">
      <el-form :model="form" label-position="top">
        <el-form-item label="案例名称">
          <el-input v-model="form.title" placeholder="例如：张三诉李四民间借贷纠纷案" />
        </el-form-item>
        <el-form-item label="案件类型">
          <el-select v-model="form.type" style="width:100%">
            <el-option label="民商事" value="民事" />
            <el-option label="刑事" value="刑事" />
            <el-option label="行政" value="行政" />
            <el-option label="知识产权" value="知识产权" />
          </el-select>
        </el-form-item>
        <el-form-item label="案件描述">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="描述案件背景、争议焦点、代理策略" />
        </el-form-item>
        <el-form-item label="案件结果">
          <el-input v-model="form.result" type="textarea" :rows="2" placeholder="如：胜诉/调解/撤诉等" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ submitting ? 'AI 包装中...' : 'AI 包装案例' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useIPStore } from '@/stores/ip'
import { ElMessage } from 'element-plus'

const ipStore = useIPStore()
const showAddDialog = ref(false)
const submitting = ref(false)

const form = reactive({
  title: '',
  type: '',
  description: '',
  result: '',
})

async function handleSubmit() {
  if (!form.title || !form.description) {
    ElMessage.warning('请填写案例名称和描述')
    return
  }
  submitting.value = true
  try {
    await ipStore.createCase({ ...form })
    ElMessage.success('案例包装成功！')
    showAddDialog.value = false
    Object.assign(form, { title: '', type: '', description: '', result: '' })
  } catch (err) {
    // 错误已处理
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.case-manager {
  max-width: 1200px;
  margin: 0 auto;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}
.page-header h2 { font-size: 22px; font-weight: 600; }
.subtitle { color: #999; font-size: 14px; margin-top: 4px; }
.empty-state { padding: 80px 0; }
</style>
