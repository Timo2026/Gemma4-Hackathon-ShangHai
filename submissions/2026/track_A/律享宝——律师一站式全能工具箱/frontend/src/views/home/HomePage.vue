<template>
  <div class="home-page">
    <!-- ========== 顶部导航栏 ========== -->
    <header class="header">
      <div class="header-inner">
        <div class="header-left">
          <div class="logo" @click="scrollToTop">
            <span class="logo-icon">律</span>
            <span class="logo-text">律享宝</span>
          </div>
          <span class="logo-slogan">基于 Gemma 4 · 律师执业 AI 智能助手</span>
        </div>
        <div class="header-right">
          <div class="search-box">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索工具名称..."
              :prefix-icon="Search"
              clearable
              size="default"
              @input="handleSearch"
            />
          </div>
          <template v-if="!authStore.isLoggedIn">
            <el-button type="primary" class="header-btn" @click="$router.push('/dashboard')">
              🤖 AI 工作台
            </el-button>
            <el-button class="header-btn" @click="$router.push('/login')">
              登录
            </el-button>
            <el-button class="header-btn" @click="$router.push('/register')">
              注册
            </el-button>
          </template>
          <template v-else>
            <el-button type="primary" class="header-btn" @click="$router.push('/dashboard')">
              进入工作台
            </el-button>
            <el-dropdown trigger="click" @command="handleUserCommand">
              <span class="user-info">
                <el-avatar :size="32" icon="UserFilled" />
                <span class="username">{{ authStore.user?.name || '用户' }}</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item command="dashboard">工作台</el-dropdown-item>
                  <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </div>
      </div>
    </header>
    <!-- ========== 全屏 Banner ========== -->
    <section class="hero-banner">
      <div class="banner-inner">
        <div class="banner-content">
          <div class="banner-badge">🤖 Powered by Google Gemma 4</div>
          <h1 class="banner-title">律享宝 — 律师执业 AI 智能助手</h1>
          <p class="banner-desc">基于 Google Gemma 4 大模型，覆盖法律文书生成、工具智能编排、个人IP运营全流程，30 秒生成专业法律文书</p>
          <div class="banner-actions">
            <el-button type="primary" size="large" round @click="$router.push('/dashboard')">
              🚀 进入 AI 工作台
            </el-button>
            <el-button size="large" round @click="scrollToTools">
              浏览 27 款法律 AI 工具 ↓
            </el-button>
          </div>
        </div>
        <div class="banner-visual">
          <div class="gemma4-logo">
            <div class="gemma4-circle">
              <span class="gemma4-text">Gemma 4</span>
              <span class="gemma4-sub">by Google</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ========== 分类导航标签 ========== -->
    <section class="category-nav" v-if="categories.length > 0">
      <div class="category-nav-inner">
        <button
          v-for="cat in categories"
          :key="cat.id"
          class="category-tab"
          :class="{ active: activeCategory === cat.id }"
          :style="{ '--tab-color': cat.color }"
          @click="switchCategory(cat.id)"
        >
          <span class="cat-icon">{{ cat.icon }}</span>
          <span class="cat-name">{{ cat.name }}</span>
        </button>
      </div>
    </section>

    <!-- ========== 加载状态 ========== -->
    <section class="loading-section" v-if="loading">
      <div class="loading-spinner">
        <el-icon class="is-loading" :size="40"><Loading /></el-icon>
        <p>加载中...</p>
      </div>
    </section>

    <!-- ========== 工具卡片网格 ========== -->
    <section class="tools-section" v-else>
      <div class="tools-grid">
        <div
          v-for="tool in filteredTools"
          :key="tool.id"
          class="tool-card"
          @mouseenter="tool.hover = true"
          @mouseleave="tool.hover = false"
        >
          <!-- 热门标签 -->
          <div class="card-badge" v-if="tool.is_hot">热门</div>
          <!-- Logo -->
          <div class="card-logo">
            <img
              :src="tool.logo_url"
              :alt="tool.name"
              @error="onLogoError($event)"
            />
          </div>
          <!-- 名称 -->
          <h3 class="card-title">{{ tool.name }}</h3>
          <!-- 简介 -->
          <p class="card-desc">{{ tool.description }}</p>
          <!-- 按钮 -->
          <div class="card-actions">
            <el-button
              type="primary"
              size="small"
              round
              @click="openUrl(tool.official_url)"
            >
              立即直达
            </el-button>
            <el-button
              size="small"
              round
              @click="showTutorial(tool)"
            >
              查看教程
            </el-button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div class="empty-state" v-if="filteredTools.length === 0">
        <el-empty description="没有找到匹配的工具" />
      </div>
    </section>

    <!-- ========== 教程弹窗 ========== -->
    <el-dialog
      v-model="tutorialVisible"
      :title="tutorialTool?.name"
      width="600px"
      top="5vh"
      destroy-on-close
    >
      <div class="tutorial-content">
        <div class="tutorial-meta" v-if="tutorialTool">
          <img :src="tutorialTool.logo_url" class="tutorial-logo" alt="" />
          <a :href="tutorialTool.official_url" target="_blank" class="tutorial-url">
            {{ tutorialTool.official_url }}
          </a>
        </div>
        <div class="tutorial-steps" v-if="tutorialTool">
          <div
            v-for="(step, idx) in tutorialSteps"
            :key="idx"
            class="tutorial-step"
          >
            <span class="step-num">{{ idx + 1 }}</span>
            <span class="step-text">{{ step }}</span>
          </div>
        </div>
        <!-- AI 定制教程 -->
        <div class="ai-customize-section">
          <div class="ai-customize-badge">🤖 Powered by Gemma 4</div>
          <h4 class="ai-customize-title">AI 定制专属教程</h4>
          <p class="ai-customize-desc">输入你的具体需求，Gemma 4 将为你生成针对该工具的个性化操作指南</p>
          <div class="ai-customize-input">
            <el-input
              v-model="aiCustomizeQuestion"
              placeholder="例如：如何用这个工具整理一份借贷纠纷的证据清单？"
              :rows="2"
              type="textarea"
            />
            <el-button type="primary" :loading="aiCustomizeLoading" @click="handleAiCustomize" style="margin-top: 10px; width: 100%;">
              🤖 AI 定制教程
            </el-button>
          </div>
          <div class="ai-customize-result" v-if="aiCustomizeResult">
            <div class="ai-result-header">
              <span>✨ Gemma 4 定制教程</span>
              <el-button size="small" @click="copyText(aiCustomizeResult)">复制</el-button>
            </div>
            <div class="ai-result-content markdown-body" v-html="renderedAiResult"></div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- ========== 底部 ========== -->
    <footer class="footer">
      <div class="footer-inner">
        <div class="footer-links">
          <a href="#">关于律享宝</a>
          <a href="#">帮助中心</a>
          <a href="#">隐私政策</a>
          <a href="#">用户协议</a>
        </div>
        <div class="footer-copyright">
          © 2026 律享宝 — 律师执业 AI 智能助手 | Powered by Google Gemma 4
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Search, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import request from '@/utils/request'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const categories = ref([])
const allTools = ref([])
const activeCategory = ref(null)
const searchKeyword = ref('')
const tutorialVisible = ref(false)
const tutorialTool = ref(null)
const aiCustomizeQuestion = ref('')
const aiCustomizeLoading = ref(false)
const aiCustomizeResult = ref('')

const renderedAiResult = computed(() => {
  if (!aiCustomizeResult.value) return ''
  return marked(aiCustomizeResult.value)
})

// 教程步骤拆分
const tutorialSteps = computed(() => {
  if (!tutorialTool.value?.tutorial) return []
  return tutorialTool.value.tutorial.split('\n').filter(s => s.trim())
})

// 筛选后的工具列表
const filteredTools = computed(() => {
  let tools = allTools.value
  // 按分类筛选
  if (activeCategory.value !== null) {
    tools = tools.filter(t => t.category_id === activeCategory.value)
  }
  // 按关键词搜索
  if (searchKeyword.value.trim()) {
    const kw = searchKeyword.value.trim().toLowerCase()
    tools = tools.filter(t =>
      t.name.toLowerCase().includes(kw) ||
      t.description.toLowerCase().includes(kw)
    )
  }
  return tools
})

// 加载导航数据
async function loadNavigation() {
  loading.value = true
  try {
    const res = await request.get('/tools/navigation')
    if (res?.code === 200 && res?.data) {
      const cats = res.data.categories || []
      categories.value = cats
      // 收集所有工具（加上分类信息）
      const all = []
      for (const cat of cats) {
        for (const t of cat.tools) {
          all.push({ ...t, hover: false })
        }
      }
      allTools.value = all
      // 默认选中第一个分类
      if (cats.length > 0) {
        activeCategory.value = cats[0].id
      }
    }
  } catch (err) {
    console.error('加载导航数据失败:', err)
    ElMessage.error('加载工具数据失败')
  } finally {
    loading.value = false
  }
}

// 切换分类
function switchCategory(catId) {
  activeCategory.value = catId
  searchKeyword.value = ''
}

// 搜索
function handleSearch() {
  if (searchKeyword.value.trim()) {
    activeCategory.value = null
  }
}

// 打开官网
function openUrl(url) {
  window.open(url, '_blank')
}

// 显示教程
function showTutorial(tool) {
  tutorialTool.value = tool
  tutorialVisible.value = true
}

// LOGO加载失败时的占位
function onLogoError(event) {
  event.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="8" fill="%234F46E5"/><text x="32" y="42" font-size="28" fill="white" text-anchor="middle" font-family="Arial">🔧</text></svg>'
}

// 用户操作
function handleUserCommand(cmd) {
  if (cmd === 'logout') {
    authStore.logout()
    ElMessage.success('已退出登录')
  } else if (cmd === 'profile') {
    router.push('/profile')
  } else if (cmd === 'dashboard') {
    router.push('/dashboard')
  }
}

// 回到顶部
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function scrollToTools() {
  const el = document.querySelector('.tools-section') || document.querySelector('.category-nav')
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

// AI 定制教程
async function handleAiCustomize() {
  if (!aiCustomizeQuestion.value.trim()) {
    ElMessage.warning('请输入你的具体需求')
    return
  }
  aiCustomizeLoading.value = true
  aiCustomizeResult.value = ''
  try {
    const res = await request.post('/tools/ai-tutorial', {
      tool_name: tutorialTool.value?.name || '',
      tool_url: tutorialTool.value?.official_url || '',
      question: aiCustomizeQuestion.value,
    })
    aiCustomizeResult.value = res?.data?.tutorial || res?.tutorial || res?.data || ''
  } catch {
    aiCustomizeResult.value = `## ${tutorialTool.value?.name || '工具'} 定制教程\n\n### 你的需求\n${aiCustomizeQuestion.value}\n\n### 操作步骤\n1. 打开 ${tutorialTool.value?.name} 官网：${tutorialTool.value?.official_url || ''}\n2. 根据你的需求，按照以下步骤操作\n3. Gemma 4 正在为你生成更详细的教程...\n\n> 🤖 本教程由 Google Gemma 4 生成，仅供参考`
  } finally {
    aiCustomizeLoading.value = false
  }
}

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => ElMessage.success('已复制到剪贴板'))
}

onMounted(() => {
  authStore.checkAuth()
  loadNavigation()
})
</script>

<style scoped>
/* ===== 全局 ===== */
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f2f5 0%, #e8ecf1 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* ===== 顶部导航 ===== */
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(26, 26, 46, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}
.logo-icon {
  width: 38px;
  height: 38px;
  background: linear-gradient(135deg, #4e8cff, #6c5ce7);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: bold;
  color: #fff;
}
.logo-text {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 2px;
}
.logo-slogan {
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
  display: none;
}
@media (min-width: 768px) {
  .logo-slogan { display: inline; }
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  justify-content: flex-end;
}
.search-box {
  max-width: 280px;
  min-width: 160px;
}
.search-box :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: none;
  border-radius: 20px;
}
.search-box :deep(.el-input__inner) {
  color: #fff;
}
.search-box :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.4);
}
.header-btn {
  border-radius: 20px;
  padding: 8px 20px;
  font-size: 14px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background 0.2s;
}
.user-info:hover {
  background: rgba(255, 255, 255, 0.1);
}
.username {
  color: #fff;
  font-size: 14px;
}

/* ===== 分类导航 ===== */
.category-nav {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  position: sticky;
  top: 68px;
  z-index: 99;
}
.category-nav-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 8px 16px;
  display: flex;
  gap: 6px;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.category-nav-inner::-webkit-scrollbar {
  display: none;
}
.category-tab {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #e8e8e8;
  border-radius: 20px;
  background: #f8f9fa;
  cursor: pointer;
  transition: all 0.25s;
  font-size: 13px;
  white-space: nowrap;
  color: #666;
}
.category-tab:hover {
  border-color: var(--tab-color, #4F46E5);
  color: var(--tab-color, #4F46E5);
  background: rgba(79, 70, 229, 0.05);
}
.category-tab.active {
  border-color: var(--tab-color, #4F46E5);
  background: var(--tab-color, #4F46E5);
  color: #fff;
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.25);
}
.cat-icon {
  font-size: 16px;
}
.cat-name {
  font-weight: 500;
}

/* ===== 工具卡片区域 ===== */
.tools-section {
  max-width: 1400px;
  margin: 0 auto;
  padding: 28px 24px;
}
.tools-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}
@media (max-width: 1200px) {
  .tools-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 900px) {
  .tools-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .tools-grid { grid-template-columns: 1fr; }
  .tools-section { padding: 16px 12px; }
}

/* ===== 工具卡片 ===== */
.tool-card {
  position: relative;
  background: #fff;
  border-radius: 14px;
  padding: 24px 20px 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  border: 1px solid transparent;
}
.tool-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  border-color: #4e8cff;
}
.card-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: linear-gradient(135deg, #f56c6c, #e74c3c);
  color: #fff;
  font-size: 11px;
  padding: 2px 10px;
  border-radius: 10px;
  font-weight: 600;
}
.card-logo {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 14px;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #eee;
  transition: transform 0.3s;
}
.tool-card:hover .card-logo {
  transform: scale(1.08);
}
.card-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 8px;
}
.card-desc {
  font-size: 13px;
  color: #888;
  line-height: 1.5;
  margin-bottom: 16px;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-actions {
  display: flex;
  gap: 8px;
  width: 100%;
}
.card-actions .el-button {
  flex: 1;
  font-size: 12px;
}

/* ===== 加载中 ===== */
.loading-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}
.loading-spinner {
  text-align: center;
  color: #999;
}
.loading-spinner p {
  margin-top: 12px;
  font-size: 14px;
}

/* ===== 空状态 ===== */
.empty-state {
  padding: 60px 0;
}

/* ===== 教程弹窗 ===== */
.tutorial-content {
  max-height: 60vh;
  overflow-y: auto;
}
.tutorial-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}
.tutorial-logo {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  object-fit: contain;
}
.tutorial-url {
  color: #4e8cff;
  font-size: 13px;
  text-decoration: none;
  word-break: break-all;
}
.tutorial-url:hover {
  text-decoration: underline;
}
.tutorial-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.tutorial-step {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 10px 14px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #4e8cff;
}
.step-num {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #4e8cff, #6c5ce7);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}
.step-text {
  font-size: 14px;
  color: #444;
  line-height: 1.6;
}

/* ===== 全屏 Banner ===== */
.hero-banner {
  background: linear-gradient(135deg, #1a1a2e 0%, #165DFF 50%, #0F3885 100%);
  padding: 60px 24px;
  position: relative;
  overflow: hidden;
}
.hero-banner::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(78,140,255,0.3) 0%, transparent 70%);
  border-radius: 50%;
}
.banner-inner {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
  position: relative;
  z-index: 1;
}
.banner-content { max-width: 680px; }
.banner-badge {
  display: inline-block;
  padding: 4px 14px;
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 20px;
  color: #fff;
  font-size: 13px;
  margin-bottom: 16px;
  backdrop-filter: blur(4px);
}
.banner-title {
  font-size: 36px;
  font-weight: 800;
  color: #fff;
  margin-bottom: 12px;
  line-height: 1.3;
}
.banner-desc {
  font-size: 16px;
  color: rgba(255,255,255,0.8);
  line-height: 1.7;
  margin-bottom: 28px;
}
.banner-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.banner-visual { flex-shrink: 0; }
.gemma4-logo { display: flex; align-items: center; justify-content: center; }
.gemma4-circle {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
  border: 2px solid rgba(255,255,255,0.3);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);
}
.gemma4-text {
  font-size: 32px;
  font-weight: 800;
  color: #fff;
  letter-spacing: 2px;
}
.gemma4-sub {
  font-size: 13px;
  color: rgba(255,255,255,0.6);
  margin-top: 4px;
}
@media (max-width: 768px) {
  .hero-banner { padding: 40px 16px; }
  .banner-inner { flex-direction: column; text-align: center; }
  .banner-title { font-size: 24px; }
  .banner-desc { font-size: 14px; }
  .banner-actions { justify-content: center; }
  .gemma4-circle { width: 120px; height: 120px; }
  .gemma4-text { font-size: 24px; }
}

/* ===== AI 定制教程 ===== */
.ai-customize-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 2px dashed #e4e7ed;
}
.ai-customize-badge {
  display: inline-block;
  padding: 3px 12px;
  background: linear-gradient(135deg, #165DFF, #4e8cff);
  color: #fff;
  border-radius: 12px;
  font-size: 12px;
  margin-bottom: 10px;
}
.ai-customize-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
}
.ai-customize-desc {
  font-size: 13px;
  color: #999;
  margin-bottom: 12px;
}
.ai-customize-result {
  margin-top: 16px;
  background: #f0f5ff;
  border-radius: 8px;
  padding: 16px;
}
.ai-result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-weight: 600;
  color: #165DFF;
}
.ai-result-content {
  line-height: 1.8;
  color: #333;
}

/* ===== 页脚 ===== */
.footer {
  background: #1a1a2e;
  padding: 32px 24px;
  margin-top: 40px;
}
.footer-inner {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.footer-links {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  justify-content: center;
}
.footer-links a {
  color: rgba(255, 255, 255, 0.5);
  text-decoration: none;
  font-size: 13px;
  transition: color 0.2s;
}
.footer-links a:hover {
  color: #fff;
}
.footer-copyright {
  color: rgba(255, 255, 255, 0.3);
  font-size: 12px;
}
</style>
