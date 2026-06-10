import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'

export const useDocumentStore = defineStore('documents', () => {
  const list = ref([])
  const loading = ref(false)
  const scenarios = ref([])

  async function fetchList() {
    loading.value = true
    try {
      const res = await request.get('/documents')
      list.value = res?.data?.items || []
    } finally {
      loading.value = false
    }
  }

  async function fetchScenarios() {
    const res = await request.get('/documents/scenarios')
    scenarios.value = res?.data?.scenarios || []
    return res
  }

  async function generate(data) {
    const res = await request.post('/documents/generate', data)
    return res
  }

  async function getDetail(id) {
    const res = await request.get(`/documents/${id}`)
    return res
  }

  return { list, loading, scenarios, fetchList, fetchScenarios, generate, getDetail }
})
