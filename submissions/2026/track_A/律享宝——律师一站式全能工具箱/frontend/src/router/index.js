import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/home/HomePage.vue'),
    meta: { noAuth: true, title: '律享宝 - 基于Google Gemma 4的律师AI工具导航' },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/Login.vue'),
    meta: { noAuth: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/login/Register.vue'),
    meta: { noAuth: true },
  },
  {
    path: '/',
    component: () => import('@/components/AppLayout.vue'),
    children: [
      {
        path: 'workbench',
        name: 'Workbench',
        component: () => import('@/views/workbench/Workbench.vue'),
        meta: { title: 'AI 工作台', icon: 'HomeFilled' },
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/workbench/Workbench.vue'),
        meta: { title: 'AI 工作台', icon: 'HomeFilled' },
      },
      {
        path: 'agent/document',
        name: 'DocumentAgent',
        component: () => import('@/views/agent/DocumentAgent.vue'),
        meta: { title: '法律文档智能生成 Agent', icon: 'Document' },
      },
      {
        path: 'agent/tool',
        name: 'ToolAgent',
        component: () => import('@/views/agent/ToolAgent.vue'),
        meta: { title: '法律工具智能编排 Agent', icon: 'Connection' },
      },
      {
        path: 'agent/ip',
        name: 'IPAgent',
        component: () => import('@/views/agent/IPAgent.vue'),
        meta: { title: '律师 IP 智能运营 Agent', icon: 'UserFilled' },
      },
      {
        path: 'documents',
        name: 'Documents',
        component: () => import('@/views/documents/DocumentList.vue'),
        meta: { title: '文书管理', icon: 'Document' },
      },
      {
        path: 'documents/generate',
        name: 'DocumentGenerate',
        component: () => import('@/views/documents/DocumentGenerate.vue'),
        meta: { title: '生成文书', icon: 'Edit' },
      },
      {
        path: 'documents/:id',
        name: 'DocumentDetail',
        component: () => import('@/views/documents/DocumentDetail.vue'),
        meta: { title: '文书详情', icon: 'Reading' },
      },
      {
        path: 'templates',
        name: 'TemplateLibrary',
        component: () => import('@/views/templates/TemplateLibrary.vue'),
        meta: { title: '文书模板库', icon: 'Notebook' },
      },
      {
        path: 'templates/:id/fill',
        name: 'TemplateFill',
        component: () => import('@/views/templates/TemplateFill.vue'),
        meta: { title: '填写文书', icon: 'Edit' },
      },
      {
        path: 'tools',
        name: 'Tools',
        component: () => import('@/views/tools/ToolCatalog.vue'),
        meta: { title: '工具中心', icon: 'Tools' },
      },
      {
        path: 'tools/orchestrate',
        name: 'ToolOrchestrate',
        component: () => import('@/views/tools/ToolOrchestrate.vue'),
        meta: { title: '工具编排', icon: 'Connection' },
      },
      {
        path: 'ip',
        name: 'IPDashboard',
        component: () => import('@/views/ip/IPDashboard.vue'),
        meta: { title: 'IP 运营', icon: 'UserFilled' },
      },
      {
        path: 'ip/profile',
        name: 'IPProfile',
        component: () => import('@/views/ip/ProfileEdit.vue'),
        meta: { title: '简介包装', icon: 'EditPen' },
      },
      {
        path: 'ip/cases',
        name: 'IPCases',
        component: () => import('@/views/ip/CaseManager.vue'),
        meta: { title: '案例管理', icon: 'FolderOpened' },
      },
      {
        path: 'ip/materials',
        name: 'IPMaterials',
        component: () => import('@/views/ip/MaterialManager.vue'),
        meta: { title: '素材管理', icon: 'Files' },
      },
      {
        path: 'ip/trust',
        name: 'IPTrust',
        component: () => import('@/views/ip/TrustManager.vue'),
        meta: { title: '信任背书', icon: 'StarFilled' },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/Profile.vue'),
        meta: { title: '个人中心', icon: 'User' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  if (to.meta.noAuth) {
    next()
    return
  }
  const authStore = useAuthStore()
  if (!authStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
