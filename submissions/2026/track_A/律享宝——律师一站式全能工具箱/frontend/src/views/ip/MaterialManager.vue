<template>
  <div class="material-manager">
    <div class="page-header">
      <div>
        <h2>素材管理</h2>
        <p class="subtitle">AI 生成普法段子、专业解读等 IP 素材</p>
      </div>
      <el-button type="primary" @click="showGenerate = true">
        <el-icon><Plus /></el-icon> 生成素材
      </el-button>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :md="8" v-for="item in materials" :key="item.id">
        <el-card shadow="hover" class="material-card">
          <div class="material-type">
            <el-tag size="small">{{ item.type }}</el-tag>
          </div>
          <h4>{{ item.title }}</h4>
          <p>{{ item.summary }}</p>
          <div class="material-footer">
            <span class="material-date">{{ dayjs(item.created_at).format('MM-DD') }}</span>
            <el-button link type="primary" size="small">查看</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card v-if="materials.length === 0" shadow="never">
      <el-empty description="暂无素材，点击「生成素材」开始创建" />
    </el-card>

    <!-- 生成素材对话框 -->
    <el-dialog v-model="showGenerate" title="AI 生成 IP 素材" width="500px">
      <el-form :model="form" label-position="top">
        <el-form-item label="素材类型">
          <el-select v-model="form.type" style="width:100%">
            <el-option label="普法段子" value="普法段子" />
            <el-option label="专业解读" value="专业解读" />
            <el-option label="办案手记" value="办案手记" />
            <el-option label="行业观点" value="行业观点" />
          </el-select>
        </el-form-item>
        <el-form-item label="主题/关键词">
          <el-input v-model="form.topic" placeholder="例如：民间借贷、借条怎么写" />
        </el-form-item>
        <el-form-item label="目标平台">
          <el-select v-model="form.platform" style="width:100%">
            <el-option label="抖音（1分钟内）" value="抖音" />
            <el-option label="小红书（图文）" value="小红书" />
            <el-option label="微信公众号" value="公众号" />
            <el-option label="知乎（专业回答）" value="知乎" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGenerate = false">取消</el-button>
        <el-button type="primary" :loading="generating" @click="handleGenerate">
          {{ generating ? 'AI 生成中...' : '🚀 AI 生成' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useIPStore } from '@/stores/ip'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'

const ipStore = useIPStore()
const showGenerate = ref(false)
const generating = ref(false)
const materials = ref([])

const form = reactive({
  type: '普法段子',
  topic: '',
  platform: '抖音',
})

async function handleGenerate() {
  if (!form.topic) {
    ElMessage.warning('请输入主题')
    return
  }
  generating.value = true
  try {
    const res = await ipStore.uploadMaterial({ ...form })
    materials.value.unshift(res)
    ElMessage.success('素材生成成功！')
    showGenerate.value = false
    form.topic = ''
  } catch (err) {
    // 错误已处理
  } finally {
    generating.value = false
  }
}

onMounted(async () => {
  try {
    materials.value = await ipStore.fetchMaterials()
  } catch (e) {
    materials.value = []
  }
})
</script>

<style scoped>
.material-manager {
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
.material-card {
  border-radius: 12px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: transform 0.2s;
}
.material-card:hover { transform: translateY(-2px); }
.material-type { margin-bottom: 8px; }
.material-card h4 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 8px;
}
.material-card p {
  color: #999;
  font-size: 13px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.material-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}
.material-date { color: #c0c4cc; font-size: 12px; }
</style>
