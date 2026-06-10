import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/utils/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  function checkAuth() {
    const t = localStorage.getItem('token')
    const u = localStorage.getItem('user')
    if (t && u) {
      token.value = t
      user.value = JSON.parse(u)
    }
  }

  async function login(phone, password) {
    const res = await request.post('/auth/login', { phone, password })
    token.value = res.access_token
    user.value = res.user
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    return res
  }

  async function register(data) {
    const res = await request.post('/auth/register', data)
    return res
  }

  async function getProfile() {
    const res = await request.get('/auth/profile')
    const userData = res.data || res
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
    return userData
  }

  async function updateProfile(name, firm, license) {
    const res = await request.put('/auth/profile', { name, firm, license })
    // 更新成功后重新获取完整用户信息
    return await getProfile()
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, user, isLoggedIn, checkAuth, login, register, getProfile, updateProfile, logout }
})
