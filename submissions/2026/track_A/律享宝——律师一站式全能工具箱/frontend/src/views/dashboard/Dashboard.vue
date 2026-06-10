<template>
  <div class="dashboard">
    <!-- 欢迎横幅 -->
    <el-card class="welcome-card" shadow="never">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1>欢迎回来，{{ authStore.user?.name || '律师' }} 👋</h1>
          <p>{{ welcomeMessage }}</p>
        </div>
        <div class="welcome-actions">
          <el-button type="primary" size="large" @click="$router.push('/documents/generate')">
            <el-icon><Edit /></el-icon> 生成法律文书
          </el-button>
          <el-button size="large" @click="$router.push('/tools/orchestrate')">
            <el-icon><Connection /></el-icon> 工具编排
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 快捷入口 -->
    <div class="quick-actions">
      <el-card v-for="item in quickActions" :key="item.path" shadow="hover" class="quick-card" @click="$router.push(item.path)">
        <el-icon :size="32" :color="item.color"><component :is="item.icon" /></el-icon>
        <span class="quick-title">{{ item.title }}</span>
        <span class="quick-desc">{{ item.desc }}</span>
      </el-card>
    </div>

    <!-- 统计数据 -->
    <el-row :gutter="20">
      <el-col :xs="12" :sm="6" v-for="stat in stats" :key="stat.label">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value" :style="{ color: stat.color }">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
          <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
            {{ stat.trend > 0 ? '+' : '' }}{{ stat.trend }}%
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近文书 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="section-header">
          <span>最近文书</span>
          <el-link type="primary" @click="$router.push('/documents')">查看全部</el-link>
        </div>
      </template>
      <div v-if="docStore.list.length === 0" class="empty-state">
        <el-empty description="暂无文书，快去生成第一份吧！">
          <el-button type="primary" @click="$router.push('/documents/generate')">生成文书</el-button>
        </el-empty>
      </div>
      <el-table v-else :data="docStore.list.slice(0, 5)" style="width: 100%" @row-click="goDetail">
        <el-table-column prop="scenario" label="文书类型" min-width="120" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'warning'" size="small">
              {{ row.status === 'completed' ? '已完成' : '生成中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="160" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDocumentStore } from '@/stores/documents'

const router = useRouter()
const authStore = useAuthStore()
const docStore = useDocumentStore()

const welcomeMessage = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好！今天有哪些案件需要处理？'
  if (hour < 18) return '下午好！工作效率满满的一天！'
  return '晚上好！记得劳逸结合哦～'
})

const quickActions = [
  { path: '/documents/generate', icon: 'EditPen', title: '文书生成', desc: 'AI 自动撰写法律文书', color: '#4e8cff' },
  { path: '/tools/orchestrate', icon: 'Connection', title: '工具编排', desc: '多工具智能协同', color: '#6c5ce7' },
  { path: '/ip', icon: 'UserFilled', title: 'IP 运营', desc: '打造律师个人品牌', color: '#00b894' },
  { path: '/documents', icon: 'FolderOpened', title: '文书管理', desc: '查看和管理所有文书', color: '#fdcb6e' },
]

const stats = [
  { label: '文书总数', value: '12', color: '#4e8cff', trend: 20 },
  { label: '使用工具', value: '8', color: '#6c5ce7', trend: 15 },
  { label: 'IP 素材', value: '6', color: '#00b894', trend: 30 },
  { label: '会员天数', value: '365', color: '#fdcb6e', trend: 0 },
]

function goDetail(row) {
  router.push(`/documents/${row.id}`)
}

onMounted(() => {
  docStore.fetchList()
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}
.welcome-card {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 16px;
}
.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}
.welcome-text h1 {
  font-size: 24px;
  color: #fff;
  margin-bottom: 8px;
}
.welcome-text p {
  color: rgba(255,255,255,0.8);
  font-size: 14px;
}
.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}
.quick-card {
  cursor: pointer;
  border-radius: 12px;
  text-align: center;
  padding: 8px;
  transition: transform 0.2s;
}
.quick-card:hover {
  transform: translateY(-4px);
}
.quick-title {
  display: block;
  font-weight: 600;
  margin: 12px 0 4px;
  font-size: 15px;
}
.quick-desc {
  color: #999;
  font-size: 12px;
}
.stat-card {
  text-align: center;
  padding: 8px;
  border-radius: 12px;
  margin-bottom: 20px;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
}
.stat-label {
  font-size: 13px;
  color: #999;
  margin: 4px 0;
}
.stat-trend {
  font-size: 12px;
}
.stat-trend.up { color: #67c23a; }
.stat-trend.down { color: #f56c6c; }
.section-card {
  border-radius: 12px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}
.empty-state {
  padding: 40px 0;
}
</style>
