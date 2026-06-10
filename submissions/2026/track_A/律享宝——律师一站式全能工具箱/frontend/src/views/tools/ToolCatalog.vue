<template>
  <div class="tool-catalog">
    <div class="page-header">
      <div>
        <h2>法律工具中心</h2>
        <p class="subtitle">12 类专业法律工具，AI 智能编排，高效处理法律事务</p>
      </div>
      <el-button type="primary" @click="$router.push('/tools/orchestrate')">
        <el-icon><Connection /></el-icon> 智能编排
      </el-button>
    </div>

    <div v-loading="toolStore.loading">
      <div v-for="group in toolStore.catalog" :key="group.category" class="tool-group">
        <h3 class="group-title">{{ group.category }}</h3>
        <div class="tool-grid">
          <el-card v-for="tool in group.items" :key="tool.id" shadow="hover" class="tool-card">
            <div class="tool-icon" :style="{ background: tool.color || '#4e8cff' }">
              <el-icon :size="24"><Tools /></el-icon>
            </div>
            <div class="tool-info">
              <h4>{{ tool.name }}</h4>
              <p>{{ tool.desc }}</p>
            </div>
            <div class="tool-meta">
              <el-tag size="small" type="info" v-for="tag in (tool.tags || [])" :key="tag">{{ tag }}</el-tag>
            </div>
            <el-button text type="primary" @click="useTool(tool)">
              立即使用 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToolStore } from '@/stores/tools'

const router = useRouter()
const toolStore = useToolStore()

function useTool(tool) {
  router.push({ path: '/tools/orchestrate', query: { toolId: tool.id } })
}

onMounted(() => {
  toolStore.fetchCatalog()
})
</script>

<style scoped>
.tool-catalog {
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
.page-header h2 {
  font-size: 22px;
  font-weight: 600;
}
.subtitle {
  color: #999;
  font-size: 14px;
  margin-top: 4px;
}
.tool-group {
  margin-bottom: 32px;
}
.group-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  padding-left: 12px;
  border-left: 3px solid var(--primary-color);
}
.tool-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.tool-card {
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s;
}
.tool-card:hover {
  transform: translateY(-2px);
}
.tool-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  color: #fff;
}
.tool-info h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}
.tool-info p {
  color: #999;
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 8px;
}
.tool-meta {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
</style>
