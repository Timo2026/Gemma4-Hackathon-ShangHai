<template>
  <el-container class="app-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isMobile ? '0' : sidebarWidth" class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="sidebar-header">
        <div class="logo" v-if="!isCollapsed">
          <span class="logo-icon">律</span>
          <span class="logo-text">律享宝</span>
        </div>
        <div class="logo logo-mini" v-else>
          <span class="logo-icon">律</span>
        </div>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :router="true"
        background-color="#1a1a2e"
        text-color="#b0b0c8"
        active-text-color="#4e8cff"
      >
        <el-menu-item index="/workbench">
          <el-icon><HomeFilled /></el-icon>
          <template #title>AI 工作台</template>
        </el-menu-item>
        <el-sub-menu index="agents">
          <template #title>
            <el-icon><MagicStick /></el-icon>
            <span>三大 Agent</span>
          </template>
          <el-menu-item index="/agent/document">
            <el-icon><Document /></el-icon>
            <template #title>文档生成 Agent</template>
          </el-menu-item>
          <el-menu-item index="/agent/tool">
            <el-icon><Connection /></el-icon>
            <template #title>工具编排 Agent</template>
          </el-menu-item>
          <el-menu-item index="/agent/ip">
            <el-icon><UserFilled /></el-icon>
            <template #title>IP 运营 Agent</template>
          </el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="documents">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>文书管理</span>
          </template>
          <el-menu-item index="/documents">文书列表</el-menu-item>
          <el-menu-item index="/documents/generate">生成文书</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="templates">
          <template #title>
            <el-icon><Notebook /></el-icon>
            <span>文书模板库</span>
          </template>
          <el-menu-item index="/templates">模板目录</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="tools">
          <template #title>
            <el-icon><Tools /></el-icon>
            <span>工具中心</span>
          </template>
          <el-menu-item index="/tools">工具目录</el-menu-item>
          <el-menu-item index="/tools/orchestrate">智能编排</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="ip">
          <template #title>
            <el-icon><UserFilled /></el-icon>
            <span>IP 运营</span>
          </template>
          <el-menu-item index="/ip">运营概览</el-menu-item>
          <el-menu-item index="/ip/profile">简介包装</el-menu-item>
          <el-menu-item index="/ip/cases">案例管理</el-menu-item>
          <el-menu-item index="/ip/materials">素材管理</el-menu-item>
          <el-menu-item index="/ip/trust">信任背书</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <template #title>个人中心</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容 -->
    <el-container>
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-button text @click="toggleSidebar" class="menu-btn">
            <el-icon :size="22"><Fold v-if="!isCollapsed" /><Expand v-else /></el-icon>
          </el-button>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click">
            <span class="user-info">
              <el-avatar :size="32" icon="UserFilled" />
              <span class="username" v-show="!isMobile">{{ authStore.user?.name || '用户' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="$router.push('/profile')">
                  <el-icon><User /></el-icon>个人中心
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 页面内容 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>

    <!-- 移动端底部导航 -->
    <el-footer class="mobile-footer" v-if="isMobile">
      <div
        v-for="item in mobileNav"
        :key="item.path"
        class="mobile-nav-item"
        :class="{ active: activeMenu.startsWith(item.path) }"
        @click="$router.push(item.path)"
      >
        <el-icon :size="22"><component :is="item.icon" /></el-icon>
        <span>{{ item.label }}</span>
      </div>
    </el-footer>
  </el-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isCollapsed = ref(false)
const isMobile = ref(window.innerWidth < 768)
const sidebarWidth = computed(() => isCollapsed.value ? '64px' : '240px')
const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta?.title || '')

const mobileNav = [
  { path: '/dashboard', icon: 'HomeFilled', label: '工作台' },
  { path: '/documents', icon: 'Document', label: '文书' },
  { path: '/tools', icon: 'Tools', label: '工具' },
  { path: '/ip', icon: 'UserFilled', label: 'IP' },
  { path: '/profile', icon: 'User', label: '我的' },
]

function toggleSidebar() {
  if (isMobile.value) return
  isCollapsed.value = !isCollapsed.value
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

window.addEventListener('resize', () => {
  isMobile.value = window.innerWidth < 768
})
</script>

<style scoped>
.app-layout {
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  background: #1a1a2e;
  transition: width 0.3s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  z-index: 100;
}
.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}
.logo-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #4e8cff, #6c5ce7);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  color: #fff;
}
.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 2px;
}
.logo-mini .logo-icon {
  margin: 0;
}
.sidebar .el-menu {
  border-right: none;
  flex: 1;
}

/* 顶部导航 */
.header {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height);
  padding: 0 20px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.menu-btn {
  font-size: 18px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.username {
  font-size: 14px;
  color: #333;
}

/* 主内容区 */
.main-content {
  background: var(--bg-color);
  overflow-y: auto;
  padding: 24px;
  height: calc(100vh - var(--header-height));
}

/* 移动端底部导航 */
.mobile-footer {
  display: none;
  height: 56px;
  background: #fff;
  border-top: 1px solid #e8e8e8;
  padding: 0;
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: -240px;
    height: 100vh;
    z-index: 1000;
    transition: left 0.3s;
  }
  .sidebar.collapsed {
    left: -240px;
  }
  .main-content {
    padding: 12px;
    padding-bottom: 68px;
    height: calc(100vh - var(--header-height) - 56px);
  }
  .mobile-footer {
    display: flex;
    justify-content: space-around;
    align-items: center;
  }
  .mobile-nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    font-size: 11px;
    color: #999;
    cursor: pointer;
    padding: 4px 8px;
  }
  .mobile-nav-item.active {
    color: var(--primary-color);
  }
}
</style>
