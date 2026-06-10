<template>
  <div class="document-list">
    <div class="page-header">
      <h2>我的文书</h2>
      <el-button type="primary" @click="$router.push('/documents/generate')">
        <el-icon><Plus /></el-icon> 生成文书
      </el-button>
    </div>

    <el-card shadow="never" class="filter-card">
      <el-form :inline="true" :model="filter" size="default">
        <el-form-item label="文书类型">
          <el-select v-model="filter.scenario" placeholder="全部类型" clearable style="width:160px">
            <el-option v-for="s in docStore.scenarios" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filter.status" placeholder="全部状态" clearable style="width:120px">
            <el-option label="已完成" value="completed" />
            <el-option label="生成中" value="pending" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="docStore.fetchList()">查询</el-button>
          <el-button @click="filter = {}; docStore.fetchList()">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" v-loading="docStore.loading">
      <div v-if="docStore.list.length === 0" class="empty-state">
        <el-empty description="暂无文书记录" />
      </div>
      <el-table v-else :data="docStore.list" style="width: 100%" @row-click="goDetail">
        <el-table-column prop="title" label="文书标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="scenario" label="类型" width="140" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'warning'" size="small">
              {{ row.status === 'completed' ? '已完成' : '生成中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">{{ dayjs(row.created_at).format('YYYY-MM-DD HH:mm') }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="goDetail(row)">查看</el-button>
            <el-button link type="danger" size="small" @click.stop="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDocumentStore } from '@/stores/documents'
import dayjs from 'dayjs'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const docStore = useDocumentStore()

const filter = reactive({})

function goDetail(row) {
  router.push(`/documents/${row.id}`)
}

function handleDelete(row) {
  ElMessageBox.confirm('确定删除此文书？', '提示').then(() => {
    // 删除逻辑（需要后端支持）
    ElMessageBox.alert('删除功能待后端实现')
  }).catch(() => {})
}

onMounted(() => {
  docStore.fetchList()
  docStore.fetchScenarios()
})
</script>

<style scoped>
.document-list {
  max-width: 1200px;
  margin: 0 auto;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.page-header h2 {
  font-size: 20px;
  font-weight: 600;
}
.filter-card {
  margin-bottom: 16px;
  border-radius: 12px;
}
.empty-state {
  padding: 60px 0;
}
</style>
