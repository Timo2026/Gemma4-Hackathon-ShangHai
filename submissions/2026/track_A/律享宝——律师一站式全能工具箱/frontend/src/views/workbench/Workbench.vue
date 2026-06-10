<template>
  <div class="workbench">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="banner-content">
        <h1>欢迎回来，{{ authStore.user?.name || '律师' }} 👋</h1>
        <p>基于 Google Gemma 4 的全链路律师执业 AI Agent</p>
      </div>
    </div>

    <!-- 三大 Agent 卡片 -->
    <div class="agent-section">
      <h2 class="section-title">🤖 三大核心 Agent</h2>
      <p class="section-desc">基于 Google Gemma 4 大模型，覆盖法律文书生成、工具智能编排、个人IP运营全流程</p>
      <div class="agent-cards">
        <div class="agent-card" @click="$router.push('/agent/document')">
          <div class="agent-icon" style="background: linear-gradient(135deg, #165DFF, #4e8cff);">📜</div>
          <div class="agent-info">
            <h3>法律文档智能生成 Agent</h3>
            <p>基于 Gemma4 多步规划推理，覆盖 21 类全执业场景，30 秒生成符合法院规范的专业法律文书</p>
          </div>
          <el-button type="primary" size="large" class="agent-btn">立即使用</el-button>
        </div>
        <div class="agent-card" @click="$router.push('/agent/tool')">
          <div class="agent-icon" style="background: linear-gradient(135deg, #059669, #34d399);">🔧</div>
          <div class="agent-info">
            <h3>法律工具智能编排 Agent</h3>
            <p>基于 Gemma4 原生函数调用，自动识别办案需求，推荐最优工具组合，生成定制化保姆级教程</p>
          </div>
          <el-button type="primary" size="large" class="agent-btn">立即使用</el-button>
        </div>
        <div class="agent-card" @click="$router.push('/agent/ip')">
          <div class="agent-icon" style="background: linear-gradient(135deg, #D97706, #fbbf24);">👤</div>
          <div class="agent-info">
            <h3>律师 IP 智能运营 Agent</h3>
            <p>基于 Gemma4 内容生成能力，一键包装个人品牌，自动生成全平台宣传素材，支持一键全域分发</p>
          </div>
          <el-button type="primary" size="large" class="agent-btn">立即使用</el-button>
        </div>
      </div>
    </div>

    <!-- Gemma4 特性一键演示专区 -->
    <div class="demo-section">
      <h2 class="section-title">⚡ Gemma 4 核心特性一键演示</h2>
      <p class="section-desc">点击按钮，自动完成全流程演示</p>
      <div class="demo-cards">
        <div class="demo-card">
          <div class="demo-badge">多步规划推理</div>
          <h4>演示 1：生成民间借贷起诉状</h4>
          <p>自动填充案件信息 → 6 步规划推理 → 生成完整起诉状</p>
          <el-button type="primary" size="large" @click="demo1" :loading="demoLoading === 1">
            🚀 开始演示
          </el-button>
        </div>
        <div class="demo-card">
          <div class="demo-badge">原生函数调用</div>
          <h4>演示 2：整理庭审录音生成质证意见</h4>
          <p>自动填充需求 → 调用工具函数 → 生成转写结果和质证意见</p>
          <el-button type="primary" size="large" @click="demo2" :loading="demoLoading === 2">
            🚀 开始演示
          </el-button>
        </div>
        <div class="demo-card">
          <div class="demo-badge">内容生成能力</div>
          <h4>演示 3：律师 IP 一键包装与分发</h4>
          <p>自动填充律师信息 → 生成全套素材 → 一键分发到朋友圈</p>
          <el-button type="primary" size="large" @click="demo3" :loading="demoLoading === 3">
            🚀 开始演示
          </el-button>
        </div>
      </div>
    </div>

    <!-- 快捷功能入口 -->
    <div class="quick-section">
      <h2 class="section-title">📌 快捷功能</h2>
      <div class="quick-grid">
        <div class="quick-item" v-for="item in quickItems" :key="item.path" @click="$router.push(item.path)">
          <el-icon :size="28" :color="item.color"><component :is="item.icon" /></el-icon>
          <span class="quick-title">{{ item.title }}</span>
          <span class="quick-desc">{{ item.desc }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Edit, Connection, UserFilled, Document, Tools } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const demoLoading = ref(0)

const quickItems = [
  { title: '文书管理', desc: '查看和管理已生成的法律文书', path: '/documents', icon: Document, color: '#165DFF' },
  { title: '工具目录', desc: '浏览 12 大分类法律 AI 工具', path: '/tools', icon: Tools, color: '#059669' },
  { title: 'IP 运营', desc: '管理律师个人品牌和宣传素材', path: '/ip', icon: UserFilled, color: '#D97706' },
  { title: '个人中心', desc: '修改个人信息和账号设置', path: '/profile', icon: UserFilled, color: '#7C3AED' },
]

function demo1() {
  demoLoading.value = 1
  router.push({
    path: '/agent/document',
    query: {
      scenario: '起诉书',
      title: '张三与李四民间借贷纠纷案',
      parties: '原告：张三，被告：李四',
      facts: '张三借给李四10万元，约定年利率15%，借期1年，李四到期未还，有借条和转账记录',
      autoGenerate: 'true',
    }
  })
}

function demo2() {
  demoLoading.value = 2
  router.push({
    path: '/agent/tool',
    query: {
      query: '我有一段30分钟的庭审录音，需要整理成文字并生成质证意见',
      autoGenerate: 'true',
    }
  })
}

function demo3() {
  demoLoading.value = 3
  router.push({
    path: '/agent/ip',
    query: {
      name: '王律师',
      firm: '北京信达律师事务所',
      specialty: '民商事诉讼、合同纠纷、公司法律顾问',
      autoGenerate: 'true',
    }
  })
}
</script>

<style scoped>
.workbench { max-width: 1200px; margin: 0 auto; }

/* 欢迎横幅 */
.welcome-banner {
  background: linear-gradient(135deg, #165DFF 0%, #0F3885 100%);
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 32px;
  color: #fff;
}
.banner-content h1 { font-size: 24px; font-weight: 700; margin-bottom: 6px; }
.banner-content p { font-size: 15px; opacity: 0.85; }

/* 通用标题 */
.section-title { font-size: 20px; font-weight: 700; margin-bottom: 6px; }
.section-desc { color: #999; font-size: 14px; margin-bottom: 20px; }

/* Agent 卡片区 */
.agent-section { margin-bottom: 32px; }
.agent-cards { display: flex; flex-direction: column; gap: 16px; }
.agent-card {
  display: flex; align-items: center; gap: 20px;
  padding: 24px; background: #fff; border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  cursor: pointer; transition: all 0.3s;
}
.agent-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
.agent-icon {
  min-width: 64px; height: 64px; border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  font-size: 32px; color: #fff;
}
.agent-info { flex: 1; }
.agent-info h3 { font-size: 20px; font-weight: 700; margin-bottom: 6px; color: #333; }
.agent-info p { font-size: 14px; color: #666; line-height: 1.6; }
.agent-btn { flex-shrink: 0; }

/* 演示专区 */
.demo-section { margin-bottom: 32px; }
.demo-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.demo-card {
  padding: 24px; background: #fff; border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08); transition: all 0.3s;
}
.demo-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
.demo-badge {
  display: inline-block; padding: 2px 10px; border-radius: 12px;
  background: linear-gradient(135deg, #165DFF, #4e8cff); color: #fff;
  font-size: 12px; margin-bottom: 10px;
}
.demo-card h4 { font-size: 16px; font-weight: 600; margin-bottom: 8px; }
.demo-card p { font-size: 13px; color: #999; margin-bottom: 16px; line-height: 1.6; }

/* 快捷功能 */
.quick-section { margin-bottom: 32px; }
.quick-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }
.quick-item {
  display: flex; flex-direction: column; align-items: center;
  padding: 20px; background: #fff; border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08); cursor: pointer;
  transition: all 0.2s; text-align: center;
}
.quick-item:hover { transform: translateY(-4px); }
.quick-title { font-weight: 600; font-size: 15px; margin-top: 10px; }
.quick-desc { color: #999; font-size: 12px; margin-top: 4px; }

@media (max-width: 768px) {
  .agent-card { flex-direction: column; text-align: center; padding: 20px; }
  .demo-cards { grid-template-columns: 1fr; }
  .welcome-banner { padding: 20px; }
  .banner-content h1 { font-size: 20px; }
}
</style>
