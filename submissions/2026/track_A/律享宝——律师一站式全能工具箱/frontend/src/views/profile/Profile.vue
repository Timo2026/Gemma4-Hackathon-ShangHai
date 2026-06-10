<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <!-- 个人信息 -->
      <el-col :xs="24" :md="8">
        <el-card shadow="never" class="profile-card">
          <div class="avatar-section">
            <el-avatar :size="80" icon="UserFilled" />
            <h3>{{ user?.name || '律师' }}</h3>
            <p class="phone">{{ user?.phone || '未绑定手机' }}</p>
            <el-tag v-if="user?.level === 'premium'" type="warning" effect="dark">高级会员</el-tag>
            <el-tag v-else type="info">普通会员</el-tag>
          </div>
          <el-divider />
          <div class="info-item">
            <span>执业证号</span>
            <span>{{ user?.license || '未填写' }}</span>
          </div>
          <div class="info-item">
            <span>律师事务所</span>
            <span>{{ user?.firm || '未填写' }}</span>
          </div>
          <div class="info-item">
            <span>注册时间</span>
            <span>{{ user?.created_at ? dayjs(user.created_at).format('YYYY-MM-DD') : '-' }}</span>
          </div>
        </el-card>
      </el-col>

      <!-- 使用统计 -->
      <el-col :xs="24" :md="16">
        <el-card shadow="never" class="section-card">
          <template #header><span class="card-title">📊 使用统计</span></template>
          <el-row :gutter="16">
            <el-col :xs="12" :sm="6" v-for="s in usageStats" :key="s.label">
              <div class="usage-stat">
                <div class="usage-value" :style="{ color: s.color }">{{ s.value }}</div>
                <div class="usage-label">{{ s.label }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <el-card shadow="never" class="section-card">
          <template #header><span class="card-title">⚙️ 设置</span></template>
          <el-form label-position="left" label-width="120px">
            <el-form-item label="姓名">
              <el-input v-model="editForm.name" />
            </el-form-item>
            <el-form-item label="律师事务所">
              <el-input v-model="editForm.firm" />
            </el-form-item>
            <el-form-item label="执业证号">
              <el-input v-model="editForm.license" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSave">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card shadow="never" class="section-card">
          <template #header><span class="card-title">🔒 账号安全</span></template>
          <el-button text type="danger" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon> 退出登录
          </el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const user = ref(authStore.user)

const editForm = reactive({
  name: user.value?.name || '',
  firm: user.value?.firm || '',
  license: user.value?.license || '',
})

const usageStats = [
  { label: '文书总数', value: '12', color: '#4e8cff' },
  { label: '工具调用', value: '28', color: '#6c5ce7' },
  { label: 'IP 素材', value: '6', color: '#00b894' },
  { label: '会员天数', value: '365', color: '#fdcb6e' },
]

async function handleSave() {
  try {
    await authStore.updateProfile(editForm.name, editForm.firm, editForm.license)
    ElMessage.success('保存成功')
  } catch (err) {
    ElMessage.warning('保存失败，请稍后重试')
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.profile-page {
  max-width: 1000px;
  margin: 0 auto;
}
.profile-card {
  border-radius: 12px;
  text-align: center;
  padding: 16px;
  margin-bottom: 20px;
}
.avatar-section h3 {
  margin-top: 16px;
  font-size: 18px;
}
.phone {
  color: #999;
  margin: 4px 0 12px;
}
.info-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 14px;
}
.info-item span:first-child { color: #999; }
.section-card {
  border-radius: 12px;
  margin-bottom: 20px;
}
.card-title { font-weight: 600; }
.usage-stat {
  text-align: center;
  padding: 16px 0;
}
.usage-value {
  font-size: 28px;
  font-weight: 700;
}
.usage-label {
  font-size: 13px;
  color: #999;
  margin-top: 4px;
}
</style>
