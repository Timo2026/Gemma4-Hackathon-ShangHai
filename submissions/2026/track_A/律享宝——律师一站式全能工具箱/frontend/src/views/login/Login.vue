<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="login-container">
        <div class="login-header">
          <div class="login-logo">
            <span class="logo-icon">律</span>
            <span class="logo-title">律享宝</span>
          </div>
          <p class="login-desc">律师执业 AI 智能助手</p>
        </div>
        <el-card shadow="never" class="login-card">
          <el-tabs v-model="activeTab" stretch>
            <el-tab-pane label="登录" name="login">
              <el-form ref="formRef" :model="form" :rules="rules" size="large" @keyup.enter="handleLogin">
                <el-form-item prop="phone">
                  <el-input v-model="form.phone" placeholder="手机号" :prefix-icon="Iphone" />
                </el-form-item>
                <el-form-item prop="password">
                  <el-input v-model="form.password" type="password" placeholder="密码" show-password :prefix-icon="Lock" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" :loading="loading" class="login-btn" @click="handleLogin">
                    {{ loading ? '登录中...' : '登录' }}
                  </el-button>
                </el-form-item>
              </el-form>
              <div class="login-footer">
                <span>还没有账号？</span>
                <el-link type="primary" @click="$router.push('/register')">立即注册</el-link>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Iphone, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeTab = ref('login')
const loading = ref(false)
const formRef = ref(null)

const form = reactive({
  phone: '13800000000',
  password: '123456',
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
}

async function handleLogin() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await authStore.login(form.phone, form.password)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (err) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}
.login-bg {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.login-bg::before {
  content: '';
  position: absolute;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(78,140,255,0.15) 0%, transparent 70%);
  top: 10%;
  left: 5%;
}
.login-bg::after {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(108,92,231,0.15) 0%, transparent 70%);
  bottom: 10%;
  right: 5%;
}
.login-container {
  width: 400px;
  max-width: 90vw;
  position: relative;
  z-index: 1;
}
.login-header {
  text-align: center;
  margin-bottom: 32px;
}
.login-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
}
.logo-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #4e8cff, #6c5ce7);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: bold;
  color: #fff;
}
.logo-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 2px;
}
.login-desc {
  color: rgba(255,255,255,0.6);
  font-size: 14px;
}
.login-card {
  border-radius: 16px;
  padding: 8px;
}
.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: 22px;
}
.login-footer {
  text-align: center;
  font-size: 14px;
  color: #999;
}
</style>
