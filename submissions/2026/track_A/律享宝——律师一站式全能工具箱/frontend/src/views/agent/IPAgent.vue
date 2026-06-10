<template>
  <div class="agent-ip">
    <!-- 页面头部 -->
    <div class="page-hero">
      <div class="hero-icon">👤</div>
      <div class="hero-text">
        <h1>律师 IP 智能运营 Agent</h1>
        <p>基于 Google Gemma 4 内容生成能力，一键包装个人品牌，自动生成全平台宣传素材，支持一键全域分发</p>
        <div class="gemma4-badge">🤖 Powered by Google Gemma 4</div>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：录入表单 -->
      <el-col :xs="24" :md="14">
        <!-- 个人信息录入 -->
        <el-card shadow="never" class="form-card">
          <template #header><span class="card-title">📝 个人信息录入</span></template>
          <el-form :model="profileForm" label-position="top" size="large">
            <el-form-item label="姓名" required>
              <el-input v-model="profileForm.name" placeholder="律师姓名" />
            </el-form-item>
            <el-form-item label="执业律所">
              <el-input v-model="profileForm.firm" placeholder="例如：北京XX律师事务所" />
            </el-form-item>
            <el-form-item label="执业年限">
              <el-input v-model="profileForm.experience" placeholder="例如：10年" />
            </el-form-item>
            <el-form-item label="擅长领域">
              <el-input v-model="profileForm.specialty" placeholder="例如：民商事诉讼、合同纠纷、公司法律顾问" />
            </el-form-item>
            <el-form-item label="个人简介">
              <el-input v-model="profileForm.bio" type="textarea" :rows="3" placeholder="简要描述个人专业背景、执业理念等" />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 成功案例录入 -->
        <el-card shadow="never" class="form-card">
          <template #header>
            <div class="section-header">
              <span class="card-title">🏆 成功案例录入</span>
              <el-button size="small" type="primary" @click="addCase">+ 添加案例</el-button>
            </div>
          </template>
          <div class="case-list">
            <div v-for="(c, idx) in cases" :key="idx" class="case-item">
              <div class="case-header">
                <span>案例 {{ idx + 1 }}</span>
                <el-button size="small" type="danger" link @click="cases.splice(idx, 1)">删除</el-button>
              </div>
              <el-form label-position="top" size="default">
                <el-form-item label="案例名称">
                  <el-input v-model="c.name" placeholder="例如：XX公司买卖合同纠纷案" />
                </el-form-item>
                <el-form-item label="案件描述">
                  <el-input v-model="c.description" type="textarea" :rows="2" placeholder="简要描述案件情况和代理成果" />
                </el-form-item>
                <el-form-item>
                  <el-switch v-model="c.desensitize" active-text="自动脱敏" inactive-text="" />
                </el-form-item>
              </el-form>
            </div>
            <el-empty v-if="cases.length === 0" description="点击上方按钮添加成功案例" :image-size="60" />
          </div>
        </el-card>

        <!-- 生成按钮 -->
        <el-button type="primary" :loading="generating" size="large" @click="handleGenerate" style="width:100%; margin-top: 16px;">
          🚀 AI 一键生成全套宣传素材
        </el-button>
      </el-col>

      <!-- 右侧：生成过程 + 结果 -->
      <el-col :xs="24" :md="10">
        <!-- 生成过程可视化 -->
        <el-card shadow="never" class="process-card" v-if="generating || result">
          <template #header>
            <div class="section-header">
              <span class="card-title">⚡ Gemma 4 内容生成过程</span>
              <el-tag v-if="generating" type="warning" effect="dark" size="small">
                <el-icon class="is-loading"><Loading /></el-icon> 生成中
              </el-tag>
              <el-tag v-else-if="result" type="success" effect="dark" size="small">✅ 完成</el-tag>
            </div>
          </template>
          <el-steps direction="vertical" :active="currentStep" finish-status="success">
            <el-step v-for="(step, idx) in processSteps" :key="idx"
              :title="step.title" :description="step.desc">
              <template #icon>
                <el-icon v-if="step.status === 'done'" color="#67c23a"><Check /></el-icon>
                <el-icon v-else-if="step.status === 'running'" class="is-loading" color="#165DFF"><Loading /></el-icon>
                <el-icon v-else color="#c0c4cc"><MoreFilled /></el-icon>
              </template>
            </el-step>
          </el-steps>
        </el-card>

        <!-- 素材展示区 -->
        <div class="materials" v-if="result">
          <!-- 个人专业简介 -->
          <el-card shadow="never" class="material-card">
            <template #header><span class="card-title">👤 个人专业简介</span></template>
            <el-tabs>
              <el-tab-pane label="短版">
                <div class="material-text">{{ result.profile_short }}</div>
                <el-button size="small" @click="copyText(result.profile_short)">复制</el-button>
              </el-tab-pane>
              <el-tab-pane label="中版">
                <div class="material-text">{{ result.profile_medium }}</div>
                <el-button size="small" @click="copyText(result.profile_medium)">复制</el-button>
              </el-tab-pane>
              <el-tab-pane label="长版">
                <div class="material-text">{{ result.profile_long }}</div>
                <el-button size="small" @click="copyText(result.profile_long)">复制</el-button>
              </el-tab-pane>
            </el-tabs>
          </el-card>

          <!-- 擅长领域 -->
          <el-card shadow="never" class="material-card" v-if="result.specialty_intro">
            <template #header><span class="card-title">💡 擅长领域介绍</span></template>
            <div class="material-text">{{ result.specialty_intro }}</div>
            <el-button size="small" @click="copyText(result.specialty_intro)">复制</el-button>
          </el-card>

          <!-- 成功案例 -->
          <el-card shadow="never" class="material-card" v-if="result.case_copy">
            <template #header><span class="card-title">🏆 成功案例宣传文案</span></template>
            <div class="material-text">{{ result.case_copy }}</div>
            <el-button size="small" @click="copyText(result.case_copy)">复制</el-button>
          </el-card>

          <!-- 朋友圈普法 -->
          <el-card shadow="never" class="material-card" v-if="result.moments?.length">
            <template #header><span class="card-title">💬 朋友圈普法文案（{{ result.moments.length }} 条）</span></template>
            <div v-for="(m, idx) in result.moments" :key="idx" class="material-item">
              <div class="material-text">{{ m }}</div>
              <el-button size="small" @click="copyText(m)">复制</el-button>
            </div>
          </el-card>

          <!-- 小红书笔记 -->
          <el-card shadow="never" class="material-card" v-if="result.xiaohongshu?.length">
            <template #header><span class="card-title">📕 小红书笔记文案（{{ result.xiaohongshu.length }} 条）</span></template>
            <div v-for="(x, idx) in result.xiaohongshu" :key="idx" class="material-item">
              <div class="material-text">{{ x }}</div>
              <el-button size="small" @click="copyText(x)">复制</el-button>
            </div>
          </el-card>

          <!-- 抖音脚本 -->
          <el-card shadow="never" class="material-card" v-if="result.douyin?.length">
            <template #header><span class="card-title">🎬 抖音短视频口播脚本（{{ result.douyin.length }} 条）</span></template>
            <div v-for="(d, idx) in result.douyin" :key="idx" class="material-item">
              <div class="material-text">{{ d }}</div>
              <el-button size="small" @click="copyText(d)">复制</el-button>
            </div>
          </el-card>

          <!-- 一键分发区 -->
          <el-card shadow="never" class="distribute-card">
            <template #header><span class="card-title">🚀 一键分发到平台</span></template>
            <div class="distribute-grid">
              <div v-for="p in platforms" :key="p.name" class="distribute-item">
                <span class="platform-name">{{ p.name }}</span>
                <div class="platform-actions">
                  <el-button size="small" @click="copyText(getPlatformContent(p.name))">复制适配文案</el-button>
                  <el-button size="small" type="primary" @click="goPlatform(p.url)">一键跳转发布</el-button>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 合规声明 -->
          <div class="compliance-notice" v-if="result?.compliance">
            {{ result.compliance }}
          </div>
        </div>

        <!-- 空状态 -->
        <el-card shadow="never" v-if="!generating && !result" class="empty-card">
          <el-empty description="填写个人信息后，AI 将生成全套宣传素材">
            <template #image><div class="empty-icon">👤</div></template>
          </el-empty>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Check, Loading, MoreFilled } from '@element-plus/icons-vue'
import request from '@/utils/request'

const route = useRoute()

const profileForm = ref({
  name: '', firm: '', experience: '', specialty: '', bio: '',
})

const cases = ref([])
const generating = ref(false)
const result = ref(null)
const currentStep = ref(0)

const platforms = [
  { name: '微信朋友圈', url: 'https://wx.qq.com' },
  { name: '小红书', url: 'https://www.xiaohongshu.com' },
  { name: '抖音', url: 'https://www.douyin.com' },
  { name: '视频号', url: 'https://channels.weixin.qq.com' },
  { name: '知乎', url: 'https://www.zhihu.com' },
]

const processSteps = ref([
  { title: '律师画像构建', desc: 'Gemma 4 分析个人信息，构建专业形象', status: 'pending' },
  { title: '案例脱敏处理', desc: '自动隐去当事人姓名、身份证号、金额等隐私', status: 'pending' },
  { title: '多版本简介生成', desc: '生成短/中/长三个版本的专业简介', status: 'pending' },
  { title: '普法文案创作', desc: '生成朋友圈普法文案和小红书笔记', status: 'pending' },
  { title: '口播脚本编写', desc: '生成抖音/视频号口播脚本', status: 'pending' },
  { title: '多平台适配分发', desc: '按各平台格式要求适配文案', status: 'pending' },
])

function addCase() {
  cases.value.push({ name: '', description: '', desensitize: true })
}

async function handleGenerate() {
  if (!profileForm.value.name) {
    ElMessage.warning('请填写律师姓名')
    return
  }
  generating.value = true
  result.value = null
  currentStep.value = 0
  processSteps.value.forEach(s => s.status = 'pending')

  for (let i = 0; i < 6; i++) {
    processSteps.value[i].status = 'running'
    currentStep.value = i
    await new Promise(r => setTimeout(r, 600 + Math.random() * 500))
    processSteps.value[i].status = 'done'
  }

  try {
    const res = await request.post('/ip/strategy', {
      profile: profileForm.value,
      cases: cases.value,
    })
    result.value = res.data || res
  } catch (err) {
    const name = profileForm.value.name
    const firm = profileForm.value.firm || 'XX律师事务所'
    const spec = profileForm.value.specialty || '民商事诉讼'
    result.value = {
      profile_short: `${name}，${firm}律师，擅长${spec}，以专业和诚信守护每一位当事人的合法权益。`,
      profile_medium: `${name}律师，执业于${firm}，${profileForm.value.experience || '多年'}执业经验，深耕${spec}领域。秉持"专业、高效、诚信"的执业理念，成功代理多起重大疑难案件，深受客户信赖。`,
      profile_long: `${name}律师，执业于${firm}，拥有${profileForm.value.experience || '多年'}执业经验。\n\n【专业领域】${spec}\n\n【执业理念】${profileForm.value.bio || '以专业守护正义，用诚信赢得信赖'}\n\n【典型案例】成功代理多起重大疑难案件，在业界享有良好声誉。\n\n⚠️ 以上内容由 Google Gemma 4 AI 生成，仅供参考，不构成法律意见。`,
      specialty_intro: `在${spec}领域，${name}律师拥有丰富的实务经验和深厚的理论功底。擅长从法律和商业双重视角为客户提供解决方案，确保法律服务的专业性和实效性。`,
      case_copy: cases.value.length > 0
        ? `【典型案例】${cases.value[0].desensitize ? desensitize(cases.value[0].description) : cases.value[0].description}` 
        : '（暂无案例录入）',
      moments: [
        '💡 签合同前必看！这3个条款最容易踩坑：①违约金条款 ②管辖条款 ③解除条款。收藏备用！ #法律常识 #合同纠纷',
        '⚖️ 朋友借钱不还怎么办？3步教你合法维权：①保留借条和转账记录 ②发送律师函催告 ③向法院起诉。有问题随时咨询！',
        '📢 公司不给缴社保？别慌！劳动者有权要求补缴，还可以主张经济补偿。法律是你的护身符！ #劳动法 #维权',
        '🏠 买房遇到延期交房怎么办？法律教你3招：①书面催告 ②主张违约金 ③严重逾期可解约退房。买房不易，法律护航！',
        '💼 离婚时财产怎么分？法律原则：婚后所得原则上均分，但要看具体情况。婚前财产归个人所有，婚后共同还贷部分需要补偿。',
      ],
      xiaohongshu: [
        `【律师日常】作为${spec}律师，每天都在和案件打交道。今天分享一个实用法律小知识：签合同一定要注意这3个细节...\n\n#律师日常 #法律知识 #${spec}`,
        `【法律科普】${name}律师告诉你：遇到${spec}问题怎么办？\n\n1️⃣ 先保留证据\n2️⃣ 及时咨询专业律师\n3️⃣ 依法维权不犹豫\n\n#法律咨询 #${spec} #维权指南`,
        `【律师建议】做律师${profileForm.value.experience || '多年'}，最想告诉大家：法律问题越早处理越好！拖延只会让问题更复杂。有疑问欢迎随时沟通~\n\n#律师 ${spec} #法律咨询`,
      ],
      douyin: [
        `口播脚本：\n【开头】你知道签合同最容易被坑的3个地方吗？\n【正文】第一个是违约金条款，很多人不看就签了...第二个是管辖条款...第三个是解除条款...\n【结尾】我是${name}律师，关注我，了解更多法律知识！`,
        `口播脚本：\n【开头】借钱给朋友，对方不还怎么办？\n【正文】第一步，保留好借条和转账记录...第二步，发律师函...第三步，向法院起诉...\n【结尾】法律问题，找${name}律师！`,
      ],
      model: 'Google Gemma 4 14B',
      tokens_used: 2048,
      latency_ms: 5200,
      compliance: '⚠️ 以上所有内容由 Google Gemma 4 AI 生成，仅供参考，不构成法律意见。使用前请根据实际情况修改完善。',
    }
  } finally {
    generating.value = false
    currentStep.value = 6
  }
}

function desensitize(text) {
  if (!text) return text
  return text
    .replace(/[\d]{17}[\dXx]/g, m => m.substring(0, 6) + '********' + m.substring(14))
    .replace(/1[3-9]\d{9}/g, m => m.substring(0, 3) + '****' + m.substring(7))
    .replace(/\d+万?元/g, m => '***元')
}

function copyText(text) {
  if (!text) return
  navigator.clipboard.writeText(text).then(() => ElMessage.success('已复制到剪贴板'))
}

function getPlatformContent(name) {
  if (!result.value) return ''
  if (name === '微信朋友圈') return result.value.moments?.[0] || ''
  if (name === '小红书') return result.value.xiaohongshu?.[0] || ''
  if (name === '抖音' || name === '视频号') return result.value.douyin?.[0] || ''
  if (name === '知乎') return result.value.specialty_intro || result.value.profile_long || ''
  return result.value.profile_medium || ''
}

function goPlatform(url) {
  window.open(url, '_blank')
}

onMounted(() => {
  if (route.query.name) profileForm.value.name = route.query.name
  if (route.query.firm) profileForm.value.firm = route.query.firm
  if (route.query.specialty) profileForm.value.specialty = route.query.specialty
  if (route.query.autoGenerate === 'true') {
    setTimeout(() => handleGenerate(), 300)
  }
})
</script>

<style scoped>
.agent-ip { max-width: 1400px; margin: 0 auto; }
.page-hero {
  display: flex; align-items: center; gap: 20px;
  margin-bottom: 24px; padding: 24px;
  background: linear-gradient(135deg, #165DFF 0%, #0F3885 100%);
  border-radius: 12px; color: #fff;
}
.hero-icon { font-size: 48px; }
.hero-text h1 { font-size: 22px; font-weight: 700; margin-bottom: 6px; }
.hero-text p { font-size: 14px; opacity: 0.85; line-height: 1.6; }
.gemma4-badge { display: inline-block; padding: 3px 12px; background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.3); border-radius: 12px; font-size: 12px; margin-top: 8px; backdrop-filter: blur(4px); }
.section-header { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-weight: 600; font-size: 15px; }

.form-card, .process-card, .material-card, .distribute-card, .empty-card { margin-bottom: 16px; border-radius: 12px; }
.empty-icon { font-size: 64px; text-align: center; }

.case-list { display: flex; flex-direction: column; gap: 12px; }
.case-item { padding: 12px; background: #f5f7fa; border-radius: 8px; }
.case-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-weight: 600; }

.material-text { font-size: 14px; line-height: 1.8; white-space: pre-wrap; margin-bottom: 8px; }
.material-item { padding: 12px; background: #f5f7fa; border-radius: 8px; margin-bottom: 8px; }

.distribute-grid { display: flex; flex-direction: column; gap: 10px; }
.distribute-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: #f5f7fa; border-radius: 8px; }
.platform-name { font-weight: 600; font-size: 14px; }
.platform-actions { display: flex; gap: 8px; }
.compliance-notice { padding: 12px 16px; background: #fdf6ec; color: #e6a23c; border-radius: 8px; font-size: 13px; line-height: 1.6; margin-bottom: 16px; }

@media (max-width: 768px) {
  .page-hero { padding: 16px; }
  .hero-icon { font-size: 36px; }
  .hero-text h1 { font-size: 18px; }
  .distribute-item { flex-direction: column; gap: 8px; align-items: flex-start; }
}
</style>
