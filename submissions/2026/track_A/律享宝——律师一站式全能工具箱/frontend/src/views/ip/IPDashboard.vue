<template>
  <div class="ip-dashboard">
    <div class="page-header">
      <h2>IP 运营中心</h2>
      <p class="subtitle">AI 辅助打造律师个人品牌，多渠道内容分发</p>
    </div>

    <!-- 运营概览 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6" v-for="s in ipStats" :key="s.label">
        <el-card shadow="never" class="stat-card">
          <div class="stat-icon" :style="{ background: s.color + '20', color: s.color }">
            <el-icon :size="24"><component :is="s.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ s.value }}</div>
            <div class="stat-label">{{ s.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷入口 -->
    <div class="ip-actions">
      <el-card v-for="item in quickActions" :key="item.path" shadow="hover" class="action-card" @click="$router.push(item.path)">
        <el-icon :size="40" :color="item.color"><component :is="item.icon" /></el-icon>
        <div class="action-info">
          <h4>{{ item.title }}</h4>
          <p>{{ item.desc }}</p>
        </div>
        <el-icon><ArrowRight /></el-icon>
      </el-card>
    </div>

    <!-- 平台分布 -->
    <el-card shadow="never">
      <template #header><span class="card-title">🌐 多平台分发</span></template>
      <el-row :gutter="16">
        <el-col :xs="12" :sm="8" :md="4" v-for="platform in platforms" :key="platform" class="platform-item">
          <el-tag size="large" style="width:100%;justify-content:center;padding:8px 0" effect="plain">
            {{ platform }}
          </el-tag>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useIPStore } from '@/stores/ip'

const router = useRouter()
const ipStore = useIPStore()
const platforms = ref([])

const quickActions = [
  { path: '/ip/profile', icon: 'EditPen', title: '简介包装', desc: 'AI 生成多平台律师简介', color: '#4e8cff' },
  { path: '/ip/cases', icon: 'FolderOpened', title: '案例管理', desc: '经典案例包装与展示', color: '#6c5ce7' },
  { path: '/ip/materials', icon: 'Files', title: '素材管理', desc: '普法段子、专业解读', color: '#00b894' },
  { path: '/ip/trust', icon: 'StarFilled', title: '信任背书', desc: '资质展示与信任建设', color: '#fdcb6e' },
]

const ipStats = [
  { label: '发布平台', value: '5', icon: 'Monitor', color: '#4e8cff' },
  { label: 'IP 素材', value: '3', icon: 'Files', color: '#6c5ce7' },
  { label: '案例', value: '2', icon: 'FolderOpened', color: '#00b894' },
  { label: '曝光量', value: '1.2w+', icon: 'TrendCharts', color: '#fdcb6e' },
]

onMounted(async () => {
  try {
    platforms.value = await ipStore.fetchPlatforms()
  } catch (e) {
    platforms.value = ['抖音', '小红书', '微信视频号', 'B站', '知乎']
  }
})
</script>

<style scoped>
.ip-dashboard {
  max-width: 1200px;
  margin: 0 auto;
}
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 22px; font-weight: 600; }
.subtitle { color: #999; font-size: 14px; margin-top: 4px; }
.stats-row { margin-bottom: 20px; }
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px;
  border-radius: 12px;
  margin-bottom: 16px;
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.stat-value { font-size: 22px; font-weight: 700; }
.stat-label { font-size: 13px; color: #999; }
.ip-actions { margin-bottom: 20px; display: grid; gap: 12px; }
.action-card {
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  border-radius: 12px;
  transition: transform 0.2s;
}
.action-card:hover { transform: translateX(4px); }
.action-info { flex: 1; }
.action-info h4 { font-size: 15px; font-weight: 600; margin-bottom: 2px; }
.action-info p { color: #999; font-size: 13px; }
.card-title { font-weight: 600; }
.platform-item { margin-bottom: 12px; }
</style>
